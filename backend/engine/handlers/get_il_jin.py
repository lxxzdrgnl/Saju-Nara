"""일진(日辰) 달력 핸들러."""

from __future__ import annotations
from engine.calc.il_jin import get_il_jin_calendar
from engine.calc.validation import validate_year_month


def handle_get_il_jin(year: int, month: int) -> dict:
    """
    특정 년·월의 일진 달력 반환.

    Args:
        year:  연도 (1900~2100)
        month: 월 (1~12)
    """
    validate_year_month(year, month)
    return get_il_jin_calendar(year, month)
