"""
Saju-Calc MCP Server — FastMCP 진입점.
순수 계산 엔진: 해석 없이 4기둥·오행·십성·신살·격국·용신 반환.
"""

from fastmcp import FastMCP
from tools.calculate_saju import handle_calculate_saju
from tools.convert_calendar import handle_convert_calendar
from tools.get_dae_un import handle_get_dae_un
from tools.get_un_flow import handle_get_un_flow
from tools.check_compatibility import handle_check_compatibility

mcp = FastMCP(name="saju-calc")


@mcp.tool()
def calculate_saju(
    birth_date: str,
    birth_time: str,
    gender: str,
    calendar: str = "solar",
    is_leap_month: bool = False,
) -> dict:
    """
    사주팔자 전체 계산.

    Args:
        birth_date:    생년월일 "YYYY-MM-DD"
        birth_time:    출생 시각 "HH:MM"
        gender:        성별 "male" | "female"
        calendar:      달력 종류 "solar" | "lunar" (기본값: solar)
        is_leap_month: 음력 윤달 여부 (기본값: false)

    Notes:
        - branch_relations: 키가 없으면 해당 관계가 존재하지 않음을 의미 (계산 실패 아님)
        - ten_gods_distribution: 퍼센트(%) — 총합 100. 가중치 = 천간 1.0 / 일반 지지 0.5 / 월지 1.5
        - yong_sin.logic_type: 용신 선정 로직 태그
          "overpowered_day_master_drain" | "weak_day_master_support" | "balanced_weakest_supplement"
    """
    return handle_calculate_saju(birth_date, birth_time, gender, calendar, is_leap_month)


@mcp.tool()
def convert_calendar(
    date: str,
    from_calendar: str,
    to_calendar: str,
    is_leap_month: bool = False,
) -> dict:
    """
    양력 ↔ 음력 변환.

    Args:
        date:          변환할 날짜 "YYYY-MM-DD"
        from_calendar: 입력 달력 "solar" | "lunar"
        to_calendar:   출력 달력 "solar" | "lunar"
        is_leap_month: 음력 윤달 여부
    """
    return handle_convert_calendar(date, from_calendar, to_calendar, is_leap_month)


@mcp.tool()
def get_dae_un(
    birth_date: str,
    birth_time: str,
    gender: str,
    calendar: str = "solar",
    is_leap_month: bool = False,
    count: int = 8,
) -> list:
    """
    대운(大運) 목록 반환 — 만세력 공식.

    Args:
        birth_date:    생년월일 "YYYY-MM-DD"
        birth_time:    출생 시각 "HH:MM"
        gender:        성별 "male" | "female"
        calendar:      달력 종류 (기본값: solar)
        is_leap_month: 윤달 여부
        count:         반환할 대운 개수 (기본값: 8)
    """
    return handle_get_dae_un(birth_date, birth_time, gender, calendar, is_leap_month, count)


@mcp.tool()
def get_un_flow(
    birth_date: str,
    birth_time: str,
    gender: str,
    calendar: str = "solar",
    is_leap_month: bool = False,
    flow_type: str = "year",
    target: str = "2025",
) -> dict:
    """
    세운·월운·시운 간지 및 일간과의 관계 계산.

    Args:
        birth_date:    생년월일
        birth_time:    출생 시각
        gender:        성별
        calendar:      달력 종류
        is_leap_month: 윤달 여부
        flow_type:     "year" | "month" | "hour"
        target:        year→"YYYY", month→"YYYY-MM", hour→"HH"
    """
    return handle_get_un_flow(
        birth_date, birth_time, gender, calendar, is_leap_month, flow_type, target
    )


@mcp.tool()
def check_compatibility(person1: dict, person2: dict) -> dict:
    """
    두 사람의 궁합 점수 계산.

    Args:
        person1: {birth_date, birth_time, gender, calendar?, is_leap_month?}
        person2: {birth_date, birth_time, gender, calendar?, is_leap_month?}
    """
    return handle_check_compatibility(person1, person2)


if __name__ == "__main__":
    mcp.run()
