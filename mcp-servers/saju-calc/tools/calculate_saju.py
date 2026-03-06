"""
calculate_saju MCP tool 핸들러.
"""

from __future__ import annotations
from datetime import datetime, timedelta
from lib.saju import calculate_saju as _calc
from lib.ten_gods import generate_ten_gods_list, calculate_ten_gods_distribution, calculate_ten_god, get_branch_ten_god
from lib.sin_sal import find_sin_sals
from lib.day_master_strength import analyze_day_master_strength
from lib.gyeok_guk import determine_gyeok_guk
from lib.yong_sin import select_yong_sin
from lib.dae_un import calculate_dae_un
from lib.twelve_wun import get_twelve_wun
from lib.validation import validate_birth_input
from data.heavenly_stems import STEMS_BY_KOREAN
from data.timezone_history import get_solar_correction_minutes, get_historical_note

# sin_sal type → priority
_SAL_PRIORITY: dict[str, str] = {
    "lucky": "medium",
    "neutral": "low",
    "unlucky": "high",
    "warning": "high",
}


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
    day_stem = saju["day_pillar"]["stem"]

    # 2. 각 기둥에 십성 + 12운성 추가
    ten_gods_list = generate_ten_gods_list(saju)
    pillars_enriched = {}
    for i, key in enumerate(["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]):
        p = saju[key]
        pillars_enriched[key] = {
            **p,
            "stem_ten_god": ten_gods_list[i],
            "branch_ten_god": get_branch_ten_god(day_stem, p["branch"]),
            "twelve_wun": get_twelve_wun(p["stem"], p["branch"]),
        }

    ten_gods_dist = calculate_ten_gods_distribution(saju)

    # 3. 신살 + priority 태그
    sin_sals = [
        {**s, "priority": _SAL_PRIORITY.get(s["type"], "low")}
        for s in find_sin_sals(saju)
    ]

    # 4. 일간 강약
    strength = analyze_day_master_strength(saju, ten_gods_dist)

    # 5. 격국
    gyeok_guk = determine_gyeok_guk(ten_gods_dist)

    # 6. 용신
    yong_sin = select_yong_sin(saju, strength, ten_gods_dist)

    # 7. 현재 대운
    dae_un_list = calculate_dae_un(saju, count=10)
    birth_year = int(birth_date.split("-")[0])
    current_age = datetime.now().year - birth_year
    current_dae_un = next(
        (d for d in dae_un_list if d["start_age"] <= current_age <= d["end_age"]),
        dae_un_list[-1],
    )
    current_dae_un = {
        **current_dae_un,
        "stem_ten_god": calculate_ten_god(day_stem, current_dae_un["stem"]),
        "branch_ten_god": get_branch_ten_god(day_stem, current_dae_un["branch"]),
    }

    # 8. 음양 비율
    all_stems = [saju[k]["stem"] for k in ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]]
    all_branches_yy = [saju[k]["yin_yang"] for k in ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]]
    stem_yy = [STEMS_BY_KOREAN[s]["yin_yang"] for s in all_stems]
    branch_yy = all_branches_yy  # branch yin_yang = stem yin_yang of branch's rep stem (simplified: use pillar yin_yang)
    all_yy = stem_yy + [saju[k]["yin_yang"] for k in ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]]
    yang_count = sum(1 for y in all_yy if y == "양")
    yin_count = 8 - yang_count
    yin_yang_ratio = {
        "yang": round(yang_count / 8 * 100, 1),
        "yin": round(yin_count / 8 * 100, 1),
    }

    # 9. meta
    hh, mm = map(int, birth_time.split(":"))
    original_dt = datetime(birth_year, *map(int, birth_date.split("-")[1:]), hh, mm)
    correction = get_solar_correction_minutes(original_dt)
    applied_dt = original_dt + timedelta(minutes=correction)
    meta = {
        "time_correction_minutes": correction,
        "applied_time": applied_dt.strftime("%Y-%m-%dT%H:%M"),
        "timezone_note": get_historical_note(original_dt),
    }

    return {
        **saju,
        **pillars_enriched,
        "ten_gods_distribution": ten_gods_dist,
        "sin_sals": sin_sals,
        "yin_yang_ratio": yin_yang_ratio,
        "day_master_strength": strength,
        "gyeok_guk": gyeok_guk,
        "yong_sin": yong_sin,
        "dae_un_start_age": dae_un_list[0]["start_age"],
        "current_dae_un": current_dae_un,
        "meta": meta,
    }
