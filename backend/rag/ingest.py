"""
knowledge/ JSON → ChromaDB 인덱싱.
각 카테고리별로 현재 스키마에 맞게 document 텍스트를 구성하여 임베딩 후 저장.
"""

from __future__ import annotations
import json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from rag.db import get_collection

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


def _build_document(entry: dict, category: str) -> str:
    """
    벡터 검색에 쓸 document 텍스트 생성.

    우선순위:
      1. embedding_context  (모든 카테고리 공통 — 검색용 한국어 맥락)
      2. core_nature / core_meaning  (1문장 본질 요약)
      3. 카테고리별 보조 텍스트
      4. consulting_points (공감·조언 문장)
    """
    parts: list[str] = []

    # 1. embedding_context (공통)
    if ctx := entry.get("embedding_context"):
        parts.append(ctx)

    # 2. 본질 요약 (1문장)
    if cn := entry.get("core_nature") or entry.get("core_meaning"):
        parts.append(cn)

    name  = entry.get("name", entry.get("element", ""))
    hanja = entry.get("hanja", "")
    if name:
        parts.append(f"{name}({hanja})" if hanja else name)

    # 3. 카테고리별 보조 텍스트
    if category == "ten_gods":
        # behavior_vector → 문자열
        if bv := entry.get("behavior_vector"):
            parts.append(" ".join(bv))
        # life_patterns 값들
        if lp := entry.get("life_patterns"):
            for domain_tags in lp.values():
                parts.append(" ".join(domain_tags))
        # decision_style
        if ds := entry.get("decision_style"):
            parts.append(" ".join(v for v in ds.values() if isinstance(v, str)))

    elif category == "wuxing":
        if pv := entry.get("personality_vector"):
            parts.append(" ".join(pv))
        if et := entry.get("engine_tags"):
            parts.append(" ".join(et))

    elif category == "sin_sal":
        if ct := entry.get("consulting_tip"):
            parts.append(ct)
        if ar := entry.get("activation_rule"):
            # activation_rule은 dict — description 필드만 추출
            desc = ar.get("description") if isinstance(ar, dict) else ar
            if desc:
                parts.append(desc)

    elif category == "structure_patterns":
        if interp := entry.get("interpretation"):
            if s := interp.get("strength"):
                parts.append(s)
            if r := interp.get("risk"):
                parts.append(r)
        if ch := entry.get("career_hint"):
            parts.append(" ".join(ch))

    elif category == "dynamics":
        if traits := entry.get("traits"):
            parts.append(" ".join(traits))
        if cv := entry.get("career_vibe"):
            # career_vibe는 list[str]
            parts.append(" ".join(cv) if isinstance(cv, list) else cv)
        if risk := entry.get("risk"):
            # risk는 list[str]
            parts.append(" ".join(risk) if isinstance(risk, list) else risk)

    elif category == "ilju":
        # ilju.json 실제 필드 구조 반영
        if pt := entry.get("psychological_traits"):
            parts.append(" ".join(pt))
        if ca := entry.get("career_affinity", {}).get("examples"):
            parts.append(" ".join(ca[:5]))
        if sp := entry.get("social_pattern"):
            parts.append(" ".join(sp))
        if rs := entry.get("relationship_style"):
            parts.append(" ".join(rs))
        st = entry.get("strength")
        if isinstance(st, list):
            parts.append(" ".join(st))
        elif isinstance(st, str):
            parts.append(st)
        if vul := entry.get("vulnerability", {}).get("trait"):
            parts.append(vul)

    # 4. interpretation_tags (Writer 힌트)
    if it := entry.get("interpretation_tags"):
        parts.append(" ".join(it))

    # 5. consulting_points
    if cp := entry.get("consulting_points"):
        if trigger := cp.get("empathy_trigger"):
            parts.append(trigger)
        if speech := cp.get("solution_speech"):
            parts.append(speech)

    return " ".join(p for p in parts if p)


def _build_metadata(entry: dict, category: str) -> dict:
    """
    ChromaDB 메타데이터 — where 필터용.
    ChromaDB는 str/int/float/bool만 허용하므로 list는 콤마 구분 문자열로 변환.
    """
    meta: dict = {"category": category}

    # 공통 식별 필드
    for key in ["id", "name", "hanja", "element", "yin_yang", "season"]:
        if val := entry.get(key):
            meta[key] = str(val)

    # ilju 전용
    if category == "ilju":
        for key in ["ilju", "stem", "branch"]:
            if val := entry.get(key):
                meta[key] = str(val)

    # 신살: type, priority
    if category == "sin_sal":
        if t := entry.get("type"):
            meta["sin_sal_type"] = t
        p = entry.get("priority")
        if p is not None:
            meta["priority"] = int(p)

    # 구조 패턴: category(하위), priority
    if category == "structure_patterns":
        if sc := entry.get("category"):
            meta["pattern_category"] = sc
        p = entry.get("priority")
        if p is not None:
            meta["priority"] = int(p)

    # 십성: category(비겁/식상/재성/관성/인성)
    if category == "ten_gods":
        if sc := entry.get("category"):
            meta["ten_god_category"] = sc

    # dynamics: trigger type
    if category == "dynamics":
        if tr := entry.get("trigger", {}).get("type"):
            meta["trigger_type"] = tr

    # engine_tags / interpretation_tags → 콤마 구분 문자열
    if et := entry.get("engine_tags"):
        meta["engine_tags"] = ",".join(et)
    if it := entry.get("interpretation_tags"):
        meta["interpretation_tags"] = ",".join(it)

    # consulting_points.tab_headline
    if cp := entry.get("consulting_points"):
        if hl := cp.get("tab_headline"):
            meta["tab_headline"] = hl

    return meta


def ingest_category(category: str) -> int:
    """
    knowledge/{category}.json → ChromaDB collection.
    기존 데이터는 upsert로 덮어씀.

    Returns:
        삽입된 문서 수
    """
    filepath = KNOWLEDGE_DIR / f"{category}.json"
    if not filepath.exists():
        raise FileNotFoundError(f"Knowledge file not found: {filepath}")

    with open(filepath, encoding="utf-8") as f:
        entries: list[dict] = json.load(f)

    col = get_collection(category)

    ids       = [e["id"] for e in entries]
    documents = [_build_document(e, category) for e in entries]
    metadatas = [_build_metadata(e, category) for e in entries]

    col.upsert(ids=ids, documents=documents, metadatas=metadatas)
    return len(entries)


def ingest_all() -> dict[str, int]:
    """
    knowledge/ 내 모든 JSON 파일 인덱싱.

    Returns:
        {category: count}
    """
    categories = sorted(p.stem for p in KNOWLEDGE_DIR.glob("*.json"))
    return {cat: ingest_category(cat) for cat in categories}


if __name__ == "__main__":
    results = ingest_all()
    for cat, count in results.items():
        print(f"  {cat}: {count}개 문서 인덱싱 완료")
