"""
사주 구조 패턴(Structure Patterns) 감지.
십성 분포 + 일간 강약 조합으로 주요 명리 패턴을 식별.
"""

from __future__ import annotations

_PATTERN_INFO: dict[str, dict] = {
    "sig_sang_saeng_jae": {
        "name": "식상생재",
        "hanja": "食傷生財",
        "desc": "창의적 표현(식상)이 재물(재성)로 직결되는 구조 — 아이디어가 곧 수입",
    },
    "gwan_in_sang_saeng": {
        "name": "관인상생",
        "hanja": "官印相生",
        "desc": "조직(관성)의 지원이 역량(인성)을 키우는 구조 — 승진·제도권 성장에 유리",
    },
    "jae_da_sin_yak": {
        "name": "재다신약",
        "hanja": "財多身弱",
        "desc": "기회는 넘치나 일간 에너지가 부족한 구조 — 욕심 조절과 선택과 집중 필요",
    },
    "gun_gyeop_jaeng_jae": {
        "name": "군겁쟁재",
        "hanja": "群劫爭財",
        "desc": "비겁 과다로 재성(재물·이성)을 두고 경쟁이 치열한 구조 — 독립·창업 지향",
    },
    "sig_sin_je_sal": {
        "name": "식신제살",
        "hanja": "食神制殺",
        "desc": "식신이 편관(칠살)을 제어하는 구조 — 창의력으로 권위와 압력을 극복",
    },
    "sang_gwan_pae_in": {
        "name": "상관패인",
        "hanja": "傷官佩印",
        "desc": "상관의 반골 기질을 인성이 다듬는 구조 — 날카로운 직관에 학식을 겸비",
    },
    "in_da_sin_gang": {
        "name": "인다신강",
        "hanja": "印多身强",
        "desc": "인성 과다로 일간이 더욱 강해진 구조 — 보호·학문·의존 성향, 독립 연습 필요",
    },
}


def detect_structure_patterns(ten_gods_dist_pct: dict, strength_level: str) -> list[dict]:
    """
    십성 분포(%) + 일간 강약 레벨 → 해당 구조 패턴 목록 반환.

    Args:
        ten_gods_dist_pct: calculate_saju의 ten_gods_distribution (퍼센트, 총합 100)
        strength_level: day_master_strength.level

    Returns:
        [{type, name, hanja, desc}, ...]
    """
    g = ten_gods_dist_pct.get

    sig_sang = g("식신", 0) + g("상관", 0)
    jae_seong = g("편재", 0) + g("정재", 0)
    gwan_sal = g("편관", 0) + g("정관", 0)
    in_seong = g("편인", 0) + g("정인", 0)
    bi_gyeop = g("비견", 0) + g("겁재", 0)
    weak = strength_level in ("weak", "very_weak")
    strong = strength_level in ("strong", "very_strong")

    matched: list[str] = []

    if sig_sang > 10 and jae_seong > 15:
        matched.append("sig_sang_saeng_jae")
    if gwan_sal > 10 and in_seong > 10:
        matched.append("gwan_in_sang_saeng")
    if jae_seong > 30 and weak:
        matched.append("jae_da_sin_yak")
    if bi_gyeop > 30 and jae_seong < 10:
        matched.append("gun_gyeop_jaeng_jae")
    if g("식신", 0) > 0 and g("편관", 0) > 0:
        matched.append("sig_sin_je_sal")
    if g("상관", 0) > 0 and in_seong > 10:
        matched.append("sang_gwan_pae_in")
    if in_seong > 30 and strong:
        matched.append("in_da_sin_gang")

    return [{"type": t, **_PATTERN_INFO[t]} for t in matched]
