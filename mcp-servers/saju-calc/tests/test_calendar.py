"""
음양력 변환 단위 테스트.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.calendar_converter import solar_to_lunar, lunar_to_solar, convert_calendar
import pytest


class TestSolarToLunar:
    def test_known_date(self):
        result = solar_to_lunar(1990, 3, 15)
        assert result["year"] == 1990
        assert isinstance(result["month"], int)
        assert isinstance(result["day"], int)
        assert isinstance(result["is_leap_month"], bool)

    def test_returns_valid_month(self):
        result = solar_to_lunar(2024, 1, 1)
        assert 1 <= result["month"] <= 12


class TestLunarToSolar:
    def test_round_trip(self):
        # 양력 → 음력 → 양력 왕복
        lunar = solar_to_lunar(1990, 3, 15)
        solar = lunar_to_solar(
            lunar["year"], lunar["month"], lunar["day"], lunar["is_leap_month"]
        )
        assert solar["year"] == 1990
        assert solar["month"] == 3
        assert solar["day"] == 15


class TestConvertCalendar:
    def test_solar_to_lunar(self):
        result = convert_calendar("1990-03-15", "solar", "lunar")
        assert result["original_date"] == "1990-03-15"
        assert "-" in result["converted_date"]

    def test_same_calendar_passthrough(self):
        result = convert_calendar("1990-03-15", "solar", "solar")
        assert result["converted_date"] == "1990-03-15"

    def test_solar_term_added(self):
        from tools.convert_calendar import handle_convert_calendar
        result = handle_convert_calendar("1990-03-15", "solar", "lunar")
        assert "solar_term" in result
        assert isinstance(result["solar_term"], str)
