"""
음양력 변환 — korean-lunar-calendar 패키지 래퍼.
"""

from __future__ import annotations
import functools
from datetime import date as Date
from korean_lunar_calendar import KoreanLunarCalendar


@functools.lru_cache(maxsize=512)
def solar_to_lunar(year: int, month: int, day: int) -> dict:
    """양력 → 음력 변환."""
    cal = KoreanLunarCalendar()
    cal.setSolarDate(year, month, day)
    return {
        "year": cal.lunarYear,
        "month": cal.lunarMonth,
        "day": cal.lunarDay,
        "is_leap_month": cal.isIntercalation,
    }


@functools.lru_cache(maxsize=512)
def lunar_to_solar(
    year: int, month: int, day: int, is_leap_month: bool = False
) -> dict:
    """음력 → 양력 변환."""
    cal = KoreanLunarCalendar()
    cal.setLunarDate(year, month, day, is_leap_month)
    solar = cal.SolarIsoFormat()  # "YYYY-MM-DD"
    sy, sm, sd = map(int, solar.split("-"))
    return {"year": sy, "month": sm, "day": sd}


def convert_calendar(
    date_str: str,
    from_calendar: str,
    to_calendar: str,
    is_leap_month: bool = False,
) -> dict:
    """
    날짜 변환 통합 함수.
    date_str: "YYYY-MM-DD"
    from_calendar / to_calendar: "solar" | "lunar"
    """
    y, m, d = map(int, date_str.split("-"))

    if from_calendar == to_calendar:
        return {
            "original_date": date_str,
            "converted_date": date_str,
            "is_leap_month": is_leap_month,
        }

    if from_calendar == "solar":
        result = solar_to_lunar(y, m, d)
        converted = f"{result['year']:04d}-{result['month']:02d}-{result['day']:02d}"
        return {
            "original_date": date_str,
            "converted_date": converted,
            "is_leap_month": result["is_leap_month"],
        }
    else:  # lunar → solar
        result = lunar_to_solar(y, m, d, is_leap_month)
        converted = f"{result['year']:04d}-{result['month']:02d}-{result['day']:02d}"
        return {
            "original_date": date_str,
            "converted_date": converted,
            "is_leap_month": is_leap_month,
        }
