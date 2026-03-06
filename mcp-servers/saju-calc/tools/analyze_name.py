from tools.calculate_saju import handle_calculate_saju
from lib.jakmeong import analyze_name
from lib.validation import validate_birth_input


def handle_analyze_name(
    name: str,
    birth_date: str,
    birth_time: str,
    gender: str,
    calendar: str = "solar",
    is_leap_month: bool = False,
) -> dict:
    """이름 오행 분석 + 용신 적합도."""
    validate_birth_input(birth_date, birth_time, gender, calendar)
    saju = handle_calculate_saju(birth_date, birth_time, gender, calendar, is_leap_month)
    yong_sin = saju["yong_sin"]["primary"]
    result = analyze_name(name, yong_sin)
    result["yong_sin"] = yong_sin
    return result
