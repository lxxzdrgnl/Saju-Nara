"""
calculate_saju MCP tool 핸들러.
"""

from __future__ import annotations
from lib.saju import calculate_saju as _calc
from lib.ten_gods import generate_ten_gods_list, calculate_ten_gods_distribution
from lib.sin_sal import find_sin_sals
from lib.day_master_strength import analyze_day_master_strength
from lib.gyeok_guk import determine_gyeok_guk
from lib.yong_sin import select_yong_sin
from lib.validation import validate_birth_input


def handle_calculate_saju(
    birth_date: str,
    birth_time: str,
    gender: str,
    calendar: str = "solar",
    is_leap_month: bool = False,
) -> dict:
    """
    사주팔자 전체 계산 — Pipeline 패턴.
    각 단계의 결과가 다음 단계의 입력으로 연결됨.
    """
    validate_birth_input(birth_date, birth_time, gender, calendar)

    # 1. 4기둥 계산
    saju = _calc(birth_date, birth_time, gender, calendar, is_leap_month)

    # 2. 십성
    ten_gods = generate_ten_gods_list(saju)
    ten_gods_dist = calculate_ten_gods_distribution(saju)

    # 3. 신살
    sin_sals = find_sin_sals(saju)

    # 4. 일간 강약
    strength = analyze_day_master_strength(saju, ten_gods_dist)

    # 5. 격국
    gyeok_guk = determine_gyeok_guk(ten_gods_dist)

    # 6. 용신
    yong_sin = select_yong_sin(saju, strength, ten_gods_dist)

    return {
        **saju,
        "ten_gods": ten_gods,
        "ten_gods_distribution": ten_gods_dist,
        "sin_sals": sin_sals,
        "day_master_strength": strength,
        "gyeok_guk": gyeok_guk,
        "yong_sin": yong_sin,
    }
