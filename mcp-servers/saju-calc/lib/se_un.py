"""
세운(歲運)·월운(月運)·시운(時運) 간지 계산.
"""

from __future__ import annotations
from data.heavenly_stems import get_stem_by_index
from data.earthly_branches import get_branch_by_index
from data.wuxing import WUXING_GENERATION, WUXING_DESTRUCTION


def _pillar(stem_idx: int, branch_idx: int) -> dict:
    stem = get_stem_by_index(stem_idx)
    branch = get_branch_by_index(branch_idx)
    return {
        "stem": stem["korean"],
        "branch": branch["korean"],
        "stem_element": stem["element"],
        "branch_element": branch["element"],
        "yin_yang": stem["yin_yang"],
    }


def calc_year_ganji(year: int) -> dict:
    """특정 연도의 세운 간지."""
    stem_idx = (year - 4) % 10
    branch_idx = (year - 4) % 12
    p = _pillar(stem_idx, branch_idx)
    p["ganji_name"] = f"{p['stem']}{p['branch']}년"
    return p


def calc_month_ganji(year: int, month: int) -> dict:
    """특정 월의 월운 간지 (절기 기준 아닌 단순 월 순서)."""
    # 인월(1월) 시작, 연간에 따른 월간 시작점
    year_stem_idx = (year - 4) % 10
    month_stem_starts = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0]
    start = month_stem_starts[year_stem_idx]
    # 1월=인월(index 0), 2월=묘월(1), ...
    m_offset = (month - 1) % 12
    stem_idx = (start + m_offset) % 10
    branch_idx = (2 + m_offset) % 12
    p = _pillar(stem_idx, branch_idx)
    p["ganji_name"] = f"{p['stem']}{p['branch']}월"
    return p


def calc_hour_ganji(day_stem: str, hour: int) -> dict:
    """특정 시간의 시운 간지."""
    from data.heavenly_stems import STEMS_BY_KOREAN
    day_stem_idx = STEMS_BY_KOREAN[day_stem]["index"]
    if hour >= 23 or hour < 1:
        branch_idx = 0
    else:
        branch_idx = (hour + 1) // 2
    stem_idx = (day_stem_idx * 2 + branch_idx) % 10
    p = _pillar(stem_idx, branch_idx)
    p["ganji_name"] = f"{p['stem']}{p['branch']}시"
    return p


def get_element_interaction(from_el: str, to_el: str) -> str:
    """두 오행의 관계 설명."""
    if from_el == to_el:
        return f"비화: {from_el}과 동일 오행"
    if WUXING_GENERATION.get(from_el) == to_el:
        return f"{from_el}생{to_el}: 용신을 생하는 기운"
    if WUXING_GENERATION.get(to_el) == from_el:
        return f"{to_el}생{from_el}: 일간을 설기하는 기운"
    if WUXING_DESTRUCTION.get(from_el) == to_el:
        return f"{from_el}극{to_el}: 용신을 극하는 기운"
    if WUXING_DESTRUCTION.get(to_el) == from_el:
        return f"{to_el}극{from_el}: 일간을 극하는 기운"
    return "중립"
