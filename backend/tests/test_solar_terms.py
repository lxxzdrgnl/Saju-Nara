"""
24절기 계산 단위 테스트.
"""


from datetime import datetime, timezone
from engine.calc.solar_terms import (
    get_solar_term_datetime,
    get_solar_terms_for_year,
    get_current_solar_term,
    get_solar_term_month_index,
    get_next_solar_term,
    get_previous_solar_term,
)
import pytest


class TestSolarTermDatetime:
    def test_chunfen_2024_is_march(self):
        # 2024년 춘분은 3월
        dt = get_solar_term_datetime(2024, "춘분")
        assert dt.month == 3

    def test_ipchun_2024_is_february(self):
        dt = get_solar_term_datetime(2024, "입춘")
        assert dt.month == 2

    def test_returns_utc(self):
        dt = get_solar_term_datetime(2024, "하지")
        assert dt.tzinfo is not None


class TestGetSolarTermsForYear:
    def test_returns_24_terms(self):
        terms = get_solar_terms_for_year(2024)
        assert len(terms) == 24

    def test_each_term_has_name_and_datetime(self):
        terms = get_solar_terms_for_year(2024)
        for t in terms:
            assert "name" in t
            assert "datetime" in t


class TestGetCurrentSolarTerm:
    def test_march_15_is_after_kyungchip(self):
        # 1990-03-15: 경칩(3월 초) 이후, 춘분(3월 하순) 이전
        dt = datetime(1990, 3, 15, 12, 0, tzinfo=timezone.utc)
        term = get_current_solar_term(dt)
        assert term in ["경칩", "춘분"]

    def test_january_1_term(self):
        dt = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        term = get_current_solar_term(dt)
        assert isinstance(term, str)
        assert len(term) > 0


class TestSolarTermMonthIndex:
    def test_ipchun_is_index_0(self):
        assert get_solar_term_month_index("입춘") == 0

    def test_usu_is_index_0(self):
        # 우수도 인월(0)
        assert get_solar_term_month_index("우수") == 0

    def test_kyungchip_is_index_1(self):
        assert get_solar_term_month_index("경칩") == 1


class TestNextPreviousTerm:
    def test_next_term_is_after_dt(self):
        dt = datetime(2024, 3, 15, 0, 0, tzinfo=timezone.utc)
        nxt = get_next_solar_term(dt)
        assert nxt["datetime"] > dt

    def test_prev_term_is_before_dt(self):
        dt = datetime(2024, 3, 15, 0, 0, tzinfo=timezone.utc)
        prv = get_previous_solar_term(dt)
        assert prv["datetime"] < dt
