"""
Synastry Engine — 두 사주 상호작용 계산.

calc1 + calc2 → interaction_tags (궁합 RAG 쿼리 seed)

상호작용 항목:
  1. 일간 천간합 여부 + 합화 오행
  2. 오행 용신 보완 관계
  3. 오행 분포 균형 (결핍 오행 상호 보완)
  4. 지지충 (기둥 간 충 관계)
  5. 일간 십성 관계 (person1 기준 person2 일간의 십성)
"""

from __future__ import annotations
from engine.calc.ten_gods import calculate_ten_god
from engine.calc.se_un import get_element_interaction

# ─── 천간합 테이블 ────────────────────────────────────────────────────────────

_STEM_HAP: dict[tuple[str, str], str] = {
    ("갑", "기"): "토", ("기", "갑"): "토",
    ("을", "경"): "금", ("경", "을"): "금",
    ("병", "신"): "수", ("신", "병"): "수",
    ("정", "임"): "목", ("임", "정"): "목",
    ("무", "계"): "화", ("계", "무"): "화",
}

# ─── 지지충 테이블 ───────────────────────────────────────────────────────────

_BRANCH_CLASH_SET: set[frozenset] = {
    frozenset({"자", "오"}), frozenset({"축", "미"}),
    frozenset({"인", "신"}), frozenset({"묘", "유"}),
    frozenset({"진", "술"}), frozenset({"사", "해"}),
}


def _get_all_branches(calc: dict) -> list[str]:
    return [calc[k]["branch"] for k in ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]]


def compute_synastry(calc1: dict, calc2: dict) -> dict:
    """
    두 사주의 궁합 상호작용을 분석하여 RAG 쿼리 태그를 생성.

    Args:
        calc1, calc2: handle_calculate_saju() 반환 dict

    Returns:
        {
          "interaction_tags": ["stem_hap_토", "yong_sin_complement", ...],
          "stem_hap": None | "토/금/수/목/화",
          "day_ten_god": "정재" (person1 기준 person2 일간의 십성),
          "clash_pairs": [("인", "신"), ...],
          "element_synergy": "상생" | "상극" | "동기" | None,
        }
    """
    tags: list[str] = []
    details: dict = {}

    stem1 = calc1["day_pillar"]["stem"]
    stem2 = calc2["day_pillar"]["stem"]
    el1   = calc1["day_pillar"]["stem_element"]
    el2   = calc2["day_pillar"]["stem_element"]

    # 1. 천간합
    hap = _STEM_HAP.get((stem1, stem2))
    details["stem_hap"] = hap
    if hap:
        tags.append(f"stem_hap_{hap}")

    # 2. 용신 보완
    ys1 = calc1["yong_sin"]["primary"]
    ys2 = calc2["yong_sin"]["primary"]
    if el2 == ys1 or el1 == ys2:
        tags.append("yong_sin_complement")
    if el1 == ys1 and el2 == ys2:
        tags.append("same_yong_sin_element")  # 서로 같은 용신 → 독립적

    # 3. 오행 결핍 상호 보완
    wx1: dict = calc1["wuxing_count"]
    wx2: dict = calc2["wuxing_count"]
    weak1 = calc1.get("weak_elements", [])
    weak2 = calc2.get("weak_elements", [])
    complement = [e for e in weak1 if e in calc2.get("dominant_elements", [])]
    complement += [e for e in weak2 if e in calc1.get("dominant_elements", [])]
    if complement:
        tags.append("element_complement")
    elif not weak1 and not weak2:
        tags.append("element_balanced_both")

    # 4. 지지충
    branches1 = _get_all_branches(calc1)
    branches2 = _get_all_branches(calc2)
    clash_pairs: list[tuple] = []
    for b1 in branches1:
        for b2 in branches2:
            if frozenset({b1, b2}) in _BRANCH_CLASH_SET:
                clash_pairs.append((b1, b2))
                tags.append(f"branch_clash_{b1}_{b2}")
    details["clash_pairs"] = clash_pairs

    # 5. 일간 십성 관계 (person1 기준)
    ten_god_rel = calculate_ten_god(stem1, stem2)
    details["day_ten_god"] = ten_god_rel
    tags.append(f"ilju_tengod_{ten_god_rel}")

    # 6. 일간 오행 상생/상극
    interaction = get_element_interaction(el1, el2)
    details["element_synergy"] = interaction
    tags.append(f"element_{interaction}")

    return {
        "interaction_tags": tags,
        **details,
    }
