from tools.calculate_saju import handle_calculate_saju
from lib.compatibility import check_compatibility
from lib.validation import validate_birth_input


def handle_check_compatibility(person1: dict, person2: dict) -> dict:
    """
    두 사람의 궁합 점수 계산.
    person1/person2: {birth_date, birth_time, gender, calendar?, is_leap_month?}
    """
    for p in (person1, person2):
        validate_birth_input(
            p["birth_date"], p["birth_time"], p["gender"],
            p.get("calendar", "solar"),
        )

    s1 = handle_calculate_saju(
        person1["birth_date"], person1["birth_time"], person1["gender"],
        person1.get("calendar", "solar"), person1.get("is_leap_month", False),
    )
    s2 = handle_calculate_saju(
        person2["birth_date"], person2["birth_time"], person2["gender"],
        person2.get("calendar", "solar"), person2.get("is_leap_month", False),
    )
    return check_compatibility(s1, s2)
