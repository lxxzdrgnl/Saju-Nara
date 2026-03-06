"""
신살(神殺) 판단 — 7종.
천을귀인·도화살·역마살·공망·화개살·원진살·귀문관살
"""

from __future__ import annotations
from data.earthly_branches import GONG_MANG_TABLE

# ─── 데이터 ────────────────────────────────────────────────────

# 천을귀인: 일간 기준 해당 지지
_CHEON_EUL_TABLE: dict[str, list[str]] = {
    "갑": ["축", "미"], "을": ["자", "신"],
    "병": ["해", "유"], "정": ["해", "유"],
    "무": ["축", "미"], "기": ["자", "신"],
    "경": ["축", "미"], "신": ["인", "오"],
    "임": ["사", "묘"], "계": ["사", "묘"],
}

# 도화살: 삼합 그룹별 도화지지
_DO_HWA_GROUPS: list[tuple[set[str], str]] = [
    ({"인", "오", "술"}, "묘"),
    ({"사", "유", "축"}, "오"),
    ({"신", "자", "진"}, "유"),
    ({"해", "묘", "미"}, "자"),
]

# 역마살: 삼합 그룹별 역마지지
_YEOK_MA_GROUPS: list[tuple[set[str], str]] = [
    ({"인", "오", "술"}, "신"),
    ({"사", "유", "축"}, "해"),
    ({"신", "자", "진"}, "인"),
    ({"해", "묘", "미"}, "사"),
]

# 화개살: 삼합 그룹별 화개지지
_HWA_GAE_GROUPS: list[tuple[set[str], str]] = [
    ({"인", "오", "술"}, "술"),
    ({"사", "유", "축"}, "축"),
    ({"신", "자", "진"}, "진"),
    ({"해", "묘", "미"}, "미"),
]

# 원진살: 충(沖) 쌍
_CHUNG_PAIRS: list[tuple[str, str]] = [
    ("자", "오"), ("축", "미"), ("인", "신"),
    ("묘", "유"), ("진", "술"), ("사", "해"),
]

# 귀문관살: 인·신·사·해 중 2개 이상
_GWI_MUN_BRANCHES: set[str] = {"인", "신", "사", "해"}


# ─── 판단 함수 ─────────────────────────────────────────────────

def _check_group_sal(
    branch_set: set[str], groups: list[tuple[set[str], str]]
) -> bool:
    for group, sal_branch in groups:
        if group & branch_set and sal_branch in branch_set:
            return True
    return False


def find_sin_sals(saju: dict) -> list[str]:
    """사주에서 해당하는 신살 목록 반환."""
    day_stem: str = saju["day_pillar"]["stem"]
    day_branch: str = saju["day_pillar"]["branch"]
    branches: list[str] = [saju[k]["branch"] for k in
                           ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]]
    branch_set = set(branches)
    result: list[str] = []

    # 천을귀인
    if any(b in branch_set for b in _CHEON_EUL_TABLE.get(day_stem, [])):
        result.append("cheon_eul_gwi_in")

    # 도화살
    if _check_group_sal(branch_set, _DO_HWA_GROUPS):
        result.append("do_hwa_sal")

    # 역마살
    if _check_group_sal(branch_set, _YEOK_MA_GROUPS):
        result.append("yeok_ma_sal")

    # 화개살
    if _check_group_sal(branch_set, _HWA_GAE_GROUPS):
        result.append("hwa_gae_sal")

    # 공망
    gong_mang = GONG_MANG_TABLE.get(day_branch, [])
    if any(b in branch_set for b in gong_mang):
        result.append("gong_mang")

    # 원진살 (충 관계)
    if any(a in branch_set and b in branch_set for a, b in _CHUNG_PAIRS):
        result.append("won_jin_sal")

    # 귀문관살
    if len(_GWI_MUN_BRANCHES & branch_set) >= 2:
        result.append("gwi_mun_gwan_sal")

    return result


SIN_SAL_INFO: dict[str, dict] = {
    "cheon_eul_gwi_in": {"name": "천을귀인", "hanja": "天乙貴人", "type": "lucky"},
    "do_hwa_sal":       {"name": "도화살",   "hanja": "桃花殺",   "type": "neutral"},
    "yeok_ma_sal":      {"name": "역마살",   "hanja": "驛馬殺",   "type": "neutral"},
    "hwa_gae_sal":      {"name": "화개살",   "hanja": "華蓋殺",   "type": "neutral"},
    "gong_mang":        {"name": "공망",     "hanja": "空亡",     "type": "unlucky"},
    "won_jin_sal":      {"name": "원진살",   "hanja": "元辰殺",   "type": "unlucky"},
    "gwi_mun_gwan_sal": {"name": "귀문관살", "hanja": "鬼門關殺", "type": "unlucky"},
}
