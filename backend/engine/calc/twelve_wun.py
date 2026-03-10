"""
12운성(十二運星) 계산.
각 천간이 각 지지에서 어떤 에너지 상태인지 반환.
"""

from __future__ import annotations

_STATES = ["장생", "목욕", "관대", "건록", "제왕", "쇠", "병", "사", "묘", "절", "태", "양"]

# 양간: 순행 시작 지지 인덱스 (자=0, 축=1, 인=2, ...)
_BRANCH_ORDER = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]
_BRANCH_IDX = {b: i for i, b in enumerate(_BRANCH_ORDER)}

# 각 양간의 장생 지지
_YANG_CHANGSEONG: dict[str, str] = {
    "갑": "해", "병": "인", "무": "인",
    "경": "사", "임": "신",
}

# 각 음간의 장생 지지 (역행)
_YIN_CHANGSEONG: dict[str, str] = {
    "을": "오", "정": "유", "기": "유",
    "신": "자", "계": "묘",
}


def get_twelve_wun(stem: str, branch: str) -> str:
    """천간(stem)이 지지(branch)에서의 12운성 반환."""
    if stem in _YANG_CHANGSEONG:
        start = _BRANCH_IDX[_YANG_CHANGSEONG[stem]]
        current = _BRANCH_IDX[branch]
        offset = (current - start) % 12
    else:
        start = _BRANCH_IDX[_YIN_CHANGSEONG[stem]]
        current = _BRANCH_IDX[branch]
        offset = (start - current) % 12  # 역행

    return _STATES[offset]
