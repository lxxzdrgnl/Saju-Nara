from engine.calc.saju import calculate_saju as _calc
from engine.calc.dae_un import calculate_dae_un
from engine.calc.validation import validate_birth_input


def handle_get_dae_un(
    birth_date: str,
    birth_time: str,
    gender: str,
    calendar: str = "solar",
    is_leap_month: bool = False,
    count: int = 8,
) -> list[dict]:
    """대운 목록 반환. 4기둥 계산만 수행 (풀 파이프라인 불필요)."""
    validate_birth_input(birth_date, birth_time, gender, calendar)
    saju = _calc(birth_date, birth_time, gender, calendar, is_leap_month)
    return calculate_dae_un(saju, count)
