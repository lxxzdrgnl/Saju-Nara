from engine.calc.saju import calculate_saju as _calc
from engine.calc.compatibility import check_compatibility
from engine.calc.models import PersonInput


def handle_check_compatibility(person1: dict, person2: dict) -> dict:
    """
    두 사람의 궁합 점수 계산.
    person1/person2: {birth_date, birth_time, gender, calendar?, is_leap_month?}
    """
    p1 = PersonInput(**person1)
    p2 = PersonInput(**person2)

    s1 = _calc(p1.birth_date, p1.birth_time, p1.gender, p1.calendar, p1.is_leap_month)
    s2 = _calc(p2.birth_date, p2.birth_time, p2.gender, p2.calendar, p2.is_leap_month)
    return check_compatibility(s1, s2)
