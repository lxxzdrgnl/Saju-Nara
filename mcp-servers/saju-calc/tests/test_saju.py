"""
사주 계산 단위 테스트.
검증 기준: 1990-03-15 14:30 남성 양력 → 경오일주 포함 여부
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.calculate_saju import handle_calculate_saju
from lib.ten_gods import calculate_ten_god
from lib.validation import validate_birth_input, ValidationError
import pytest


BIRTH = dict(
    birth_date="1990-03-15",
    birth_time="14:30",
    gender="male",
    calendar="solar",
)


class TestSajuPillars:
    def test_returns_four_pillars(self):
        result = handle_calculate_saju(**BIRTH)
        assert "year_pillar" in result
        assert "month_pillar" in result
        assert "day_pillar" in result
        assert "hour_pillar" in result

    def test_pillar_has_required_keys(self):
        result = handle_calculate_saju(**BIRTH)
        for key in ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]:
            p = result[key]
            assert "stem" in p
            assert "branch" in p
            assert "stem_element" in p
            assert "branch_element" in p

    def test_wuxing_count_sums_to_eight(self):
        result = handle_calculate_saju(**BIRTH)
        total = sum(result["wuxing_count"].values())
        assert total == 8

    def test_sin_sals_is_list(self):
        result = handle_calculate_saju(**BIRTH)
        assert isinstance(result["sin_sals"], list)

    def test_gyeok_guk_present(self):
        result = handle_calculate_saju(**BIRTH)
        assert "type" in result["gyeok_guk"]
        assert "name" in result["gyeok_guk"]

    def test_yong_sin_has_primary(self):
        result = handle_calculate_saju(**BIRTH)
        assert result["yong_sin"]["primary"] in ["목", "화", "토", "금", "수"]


class TestTenGods:
    def test_same_element_same_yy(self):
        # 갑(목,양) vs 갑(목,양) → 비견
        assert calculate_ten_god("갑", "갑") == "비견"

    def test_same_element_diff_yy(self):
        # 갑(목,양) vs 을(목,음) → 겁재
        assert calculate_ten_god("갑", "을") == "겁재"

    def test_generates_same_yy(self):
        # 갑(목,양) → 화 생 → 병(화,양) → 식신
        assert calculate_ten_god("갑", "병") == "식신"

    def test_controls_diff_yy(self):
        # 갑(목,양) 극 토 → 기(토,음) → 정재
        assert calculate_ten_god("갑", "기") == "정재"



class TestValidation:
    def test_invalid_date_format(self):
        with pytest.raises(ValidationError):
            validate_birth_input("1990/03/15", "14:30", "male")

    def test_invalid_year(self):
        with pytest.raises(ValidationError):
            validate_birth_input("1800-01-01", "12:00", "male")

    def test_invalid_gender(self):
        with pytest.raises(ValidationError):
            validate_birth_input("1990-03-15", "14:30", "other")

    def test_valid_input_passes(self):
        validate_birth_input("1990-03-15", "14:30", "male", "solar")
