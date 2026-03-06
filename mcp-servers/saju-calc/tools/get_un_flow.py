"""
get_un_flow — 세운·월운·시운·일진 간지 계산.
"""

from __future__ import annotations
from tools.calculate_saju import handle_calculate_saju
from lib.se_un import calc_year_ganji, calc_month_ganji, calc_hour_ganji, get_element_interaction
from lib.validation import validate_birth_input


def handle_get_un_flow(
    birth_date: str,
    birth_time: str,
    gender: str,
    calendar: str = "solar",
    is_leap_month: bool = False,
    flow_type: str = "year",
    target: str = "2025",
) -> dict:
    """
    Args:
        flow_type: "year" | "month" | "hour"
        target:
            year  → "YYYY"
            month → "YYYY-MM"
            hour  → "HH"  (당일 시운, 일주는 별도 계산)
    """
    validate_birth_input(birth_date, birth_time, gender, calendar)
    saju = handle_calculate_saju(birth_date, birth_time, gender, calendar, is_leap_month)

    day_element = saju["day_pillar"]["stem_element"]
    yong_sin = saju["yong_sin"]["primary"]

    if flow_type == "year":
        year = int(target)
        ganji = calc_year_ganji(year)
    elif flow_type == "month":
        year, month = map(int, target.split("-"))
        ganji = calc_month_ganji(year, month)
    elif flow_type == "hour":
        day_stem = saju["day_pillar"]["stem"]
        hour = int(target)
        ganji = calc_hour_ganji(day_stem, hour)
    else:
        raise ValueError(f"flow_type은 year|month|hour: {flow_type}")

    ganji["interaction_with_day_master"] = get_element_interaction(
        ganji["stem_element"], day_element
    )
    ganji["interaction_with_yong_sin"] = get_element_interaction(
        ganji["stem_element"], yong_sin
    )
    return ganji
