"""
RAG 검색 tool 핸들러.

Tool 분류:
  - search_knowledge        : 범용 자연어 시맨틱 검색
  - search_by_context       : calc 출력(context_ranking, life_domains) → Writer용 RAG 결과 조립
  - get_ilju_profile        : 일주 직접 조회 (벡터 검색 불필요)
  - get_ten_god_profile     : 십성 직접 조회
  - get_structure_pattern   : 구조 패턴 직접 조회
  - get_sin_sal_profile     : 신살 직접 조회
"""

from __future__ import annotations
import json
import functools
from pathlib import Path
from rag.db import search, search_multi, COLLECTIONS

_KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


# ─── 직접 조회 헬퍼 ────────────────────────────────────────────────────

@functools.lru_cache(maxsize=16)
def _load_knowledge(category: str) -> tuple[dict, ...]:
    """JSON 파일 파싱 결과를 메모리에 캐싱 (프로세스 수명 동안 유지)."""
    filepath = _KNOWLEDGE_DIR / f"{category}.json"
    if not filepath.exists():
        return ()
    with open(filepath, encoding="utf-8") as f:
        return tuple(json.load(f))


def _find_by_field(category: str, field: str, value: str) -> dict | None:
    for entry in _load_knowledge(category):  # tuple[dict, ...]
        if entry.get(field) == value:
            return entry
    return None


# ─── 범용 시맨틱 검색 ───────────────────────────────────────────────────

def handle_search_knowledge(
    query: str,
    categories: list[str] | None = None,
    n_results: int = 3,
    where: dict | None = None,
) -> dict:
    """
    지식 베이스 시맨틱 검색.

    Returns:
        {category: [{id, document, metadata, distance}]}
    """
    if categories and len(categories) == 1 and where is None:
        results = search(categories[0], query, n_results)
        return {categories[0]: results}
    return search_multi(query, categories, n_results)


# ─── calc 출력 → Writer용 RAG 결과 조립 ────────────────────────────────

def handle_search_by_context(
    context_ranking: dict,
    life_domains: dict,
    day_pillar: str | None = None,
    concern: str | None = None,
    n_per_domain: int = 2,
) -> dict:
    """
    saju-calc 출력(context_ranking + life_domains) → Writer용 RAG 청크 조립.

    Args:
        context_ranking : calc의 context_ranking 필드
                          {"primary_context": [{id, type, score}], "secondary_context": [...]}
        life_domains    : calc의 life_domains 필드
                          {"career": [...], "relationship": [...], "wealth": [...], "personality": [...]}
        day_pillar      : 일주 간지 (예: "경오") — ilju 직접 조회용
        concern         : 사용자 고민 원문 — concern 시맨틱 검색에 추가
        n_per_domain    : 도메인별 시맨틱 검색 결과 수 (기본 2)

    Returns:
        {
          "career":       [RAG chunk, ...],
          "relationship": [RAG chunk, ...],
          "wealth":       [RAG chunk, ...],
          "personality":  [RAG chunk, ...],
          "context":      [RAG chunk, ...],   # primary_context 직접 조회
          "ilju":         {일주 전체 지식} or None,
          "concern":      [RAG chunk, ...]    # concern 기반 검색 (있을 때)
        }
    """
    result: dict = {
        "career": [], "relationship": [], "wealth": [], "personality": [],
        "context": [], "ilju": None, "concern": [],
    }

    # 1. life_domain별 시맨틱 검색 (ten_gods + structure_patterns + wuxing)
    domain_collections = ["ten_gods", "structure_patterns", "wuxing"]
    for domain, tags in life_domains.items():
        if domain not in result or not tags:
            continue
        query = " ".join(tags[:4])  # 상위 4개 태그를 쿼리로
        chunks = []
        for col in domain_collections:
            hits = search(col, query, n_per_domain)
            chunks.extend(hits)
        # distance 기준 정렬, 상위 n_per_domain * 2개 유지
        chunks.sort(key=lambda x: x.get("distance") or 1.0)
        result[domain] = chunks[: n_per_domain * 2]

    # 2. primary_context / secondary_context 직접 조회
    all_ctx = (
        context_ranking.get("primary_context", []) +
        context_ranking.get("secondary_context", [])
    )
    for ctx in all_ctx:
        ctx_id   = ctx.get("id", "")
        ctx_type = ctx.get("type", "")
        if ctx_type == "pattern":
            entry = handle_get_structure_pattern(ctx_id)   # sp_ prefix 자동 처리
        elif ctx_type == "sin_sal":
            entry = _find_by_field("sin_sal", "name", ctx_id)
        else:
            entry = None
        if entry:
            result["context"].append({"id": ctx_id, "type": ctx_type, "data": entry})

    # 3. 일주 직접 조회
    if day_pillar:
        result["ilju"] = _find_by_field("ilju", "ilju", day_pillar)

    # 4. concern 시맨틱 검색 (있을 때)
    if concern:
        concern_chunks = search_multi(concern, ["ten_gods", "sin_sal", "ilju"], 2)
        for hits in concern_chunks.values():
            result["concern"].extend(hits)
        result["concern"].sort(key=lambda x: x.get("distance") or 1.0)
        result["concern"] = result["concern"][:4]

    return result


# ─── 직접 조회 핸들러 ───────────────────────────────────────────────────

def handle_get_ilju_profile(ilju: str) -> dict | None:
    """일주(예: '경오') 전체 지식 직접 조회."""
    return _find_by_field("ilju", "ilju", ilju)


def handle_get_ten_god_profile(ten_god_name: str) -> dict | None:
    """십성 이름으로 전체 지식 직접 조회."""
    return _find_by_field("ten_gods", "name", ten_god_name)


def handle_get_structure_pattern(pattern_id: str) -> dict | None:
    """
    구조 패턴 id로 전체 지식 직접 조회.

    calc 출력(예: 'sig_sang_saeng_jae')과 RAG 파일 id(예: 'sp_sig_sang_saeng_jae') 모두 처리.
    """
    # calc는 prefix 없이 반환하므로 'sp_' 자동 보완
    result = _find_by_field("structure_patterns", "id", pattern_id)
    if result is None:
        result = _find_by_field("structure_patterns", "id", f"sp_{pattern_id}")
    return result


def handle_get_sin_sal_profile(sin_sal_name: str) -> dict | None:
    """신살 이름으로 전체 지식 직접 조회 (예: '역마살', '귀문관살')."""
    return _find_by_field("sin_sal", "name", sin_sal_name)
