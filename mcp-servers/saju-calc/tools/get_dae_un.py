from tools.calculate_saju import handle_calculate_saju
from lib.dae_un import calculate_dae_un
from lib.validation import validate_birth_input


def handle_get_dae_un(
    birth_date: str,
    birth_time: str,
    gender: str,
    calendar: str = "solar",
    is_leap_month: bool = False,
    count: int = 8,
) -> list[dict]:
    """대운 목록 반환."""
    validate_birth_input(birth_date, birth_time, gender, calendar)
    saju = handle_calculate_saju(birth_date, birth_time, gender, calendar, is_leap_month)
    return calculate_dae_un(saju, count)
