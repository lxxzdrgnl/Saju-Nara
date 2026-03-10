"""
궁합(宮合) 점수 계산.
일주·오행·지지 관계·십성 4개 항목 가중 합산.
"""

from __future__ import annotations
from engine.data.earthly_branches import SAM_HAP, CHUNG_PAIRS
from engine.data.wuxing import WUXING_GENERATION, WUXING_DESTRUCTION


def _element_harmony(el1: str, el2: str) -> int:
    """두 오행의 조화도 (0~100)."""
    if el1 == el2:
        return 70
    if WUXING_GENERATION.get(el1) == el2 or WUXING_GENERATION.get(el2) == el1:
        return 85
    if WUXING_DESTRUCTION.get(el1) == el2 or WUXING_DESTRUCTION.get(el2) == el1:
        return 40
    return 60


def _day_pillar_score(saju1: dict, saju2: dict) -> int:
    """일주 간지 조화도."""
    el1 = saju1["day_pillar"]["stem_element"]
    el2 = saju2["day_pillar"]["stem_element"]
    base = _element_harmony(el1, el2)

    # 같은 일주면 -10 (자형)
    if saju1["day_pillar"]["stem"] == saju2["day_pillar"]["stem"] and \
       saju1["day_pillar"]["branch"] == saju2["day_pillar"]["branch"]:
        base -= 10
    return min(100, max(0, base))


def _element_harmony_score(saju1: dict, saju2: dict) -> int:
    """전체 오행 분포 조화도."""
    w1 = saju1["wuxing_count"]
    w2 = saju2["wuxing_count"]
    # 두 사주의 오행 합계 분포 균형도
    combined = {e: w1.get(e, 0) + w2.get(e, 0) for e in ["목", "화", "토", "금", "수"]}
    total = sum(combined.values()) or 1
    avg = total / 5
    variance = sum((v - avg) ** 2 for v in combined.values()) / 5
    # 분산이 낮을수록 균형 → 점수 높음
    score = max(0, 100 - int(variance * 5))
    return score


def _branch_relation_score(saju1: dict, saju2: dict) -> tuple[int, list[str]]:
    """지지 관계 점수 + 충 쌍 목록."""
    branches = [
        saju1["year_pillar"]["branch"], saju1["month_pillar"]["branch"],
        saju1["day_pillar"]["branch"],  saju1["hour_pillar"]["branch"],
        saju2["year_pillar"]["branch"], saju2["month_pillar"]["branch"],
        saju2["day_pillar"]["branch"],  saju2["hour_pillar"]["branch"],
    ]
    branch_set = set(branches)
    score = 70

    # 삼합이 성립하면 +10
    for data in SAM_HAP.values():
        if all(b in branch_set for b in data["branches"]):
            score += 10
            break

    # 충 쌍마다 -10
    conflicts = []
    for a, b in CHUNG_PAIRS:
        if a in branch_set and b in branch_set:
            score -= 10
            conflicts.append(f"{a}-{b}")

    return min(100, max(0, score)), conflicts


def _ten_gods_score(saju1: dict, saju2: dict) -> int:
    """십성 상호 관계 점수."""
    el1 = saju1["day_pillar"]["stem_element"]
    el2 = saju2["day_pillar"]["stem_element"]
    return _element_harmony(el1, el2)


def check_compatibility(saju1: dict, saju2: dict) -> dict:
    """
    궁합 점수 계산.

    Returns:
        total_score, day_pillar_score, element_harmony_score,
        branch_relation_score, ten_gods_score,
        conflict_branches, complement_elements
    """
    dp = _day_pillar_score(saju1, saju2)
    eh = _element_harmony_score(saju1, saju2)
    br, conflicts = _branch_relation_score(saju1, saju2)
    tg = _ten_gods_score(saju1, saju2)

    # 가중 평균 (40 : 25 : 20 : 15)
    total = int(dp * 0.40 + eh * 0.25 + br * 0.20 + tg * 0.15)

    # 서로 보완하는 오행 (약한 오행을 상대가 가진 경우)
    weak1 = saju1.get("weak_elements", [])
    strong2 = saju2.get("dominant_elements", [])
    complement = list(set(weak1) & set(strong2))

    return {
        "total_score": total,
        "day_pillar_score": dp,
        "element_harmony_score": eh,
        "branch_relation_score": br,
        "ten_gods_score": tg,
        "conflict_branches": conflicts,
        "complement_elements": complement,
    }
