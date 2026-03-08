"""
격국(格局) 판단 — 13종.
월지 지장간 투출 십성 기반 + 특수 종격(從格) 판단.
"""

from __future__ import annotations

# 십성 → 격국 매핑
_TEN_GOD_TO_GYEOK: dict[str, str] = {
    "정관": "jeong_gwan",
    "정재": "jeong_jae",
    "식신": "sig_sin",
    "정인": "jeong_in",
    "상관": "sang_gwan",
    "편인": "pyeon_in",
    "편재": "pyeon_jae",
    "편관": "chil_sal",
    "비견": "bi_gyeon",
    "겁재": "geob_jae",
}

GYEOK_GUK_INFO: dict[str, dict] = {
    "jeong_gwan": {"name": "정관격", "hanja": "正官格",
                   "description": "책임감·명예를 중시하는 리더형"},
    "jeong_jae":  {"name": "정재격", "hanja": "正財格",
                   "description": "성실·안정·근면한 재물 관리형"},
    "sig_sin":    {"name": "식신격", "hanja": "食神格",
                   "description": "낙천적이고 창의적인 표현형"},
    "jeong_in":   {"name": "정인격", "hanja": "正印格",
                   "description": "학구적이고 사려 깊은 지식 추구형"},
    "sang_gwan":  {"name": "상관격", "hanja": "傷官格",
                   "description": "비판적·독창적이고 자유로운 개혁형"},
    "pyeon_in":   {"name": "편인격", "hanja": "偏印格",
                   "description": "독특한 직관과 신비로운 특수 재능형"},
    "pyeon_jae":  {"name": "편재격", "hanja": "偏財格",
                   "description": "사교적이고 사업 수완이 뛰어난 활동형"},
    "chil_sal":   {"name": "칠살격", "hanja": "七殺格",
                   "description": "강한 추진력과 승부욕의 리더형"},
    "bi_gyeon":   {"name": "비견격", "hanja": "比肩格",
                   "description": "독립심·자존심이 강한 자립형"},
    "geob_jae":   {"name": "겁재격", "hanja": "劫財格",
                   "description": "경쟁심·야망이 강한 도전형"},
    "jong_wang":  {"name": "종왕격", "hanja": "從旺格",
                   "description": "비겁이 극강한 특수 격국 — 강함을 따름"},
    "jong_sal":   {"name": "종살격", "hanja": "從殺格",
                   "description": "관살이 극강한 특수 격국 — 권위를 따름"},
    "jong_jae":   {"name": "종재격", "hanja": "從財格",
                   "description": "재성이 극강한 특수 격국 — 재물을 따름"},
    "balanced":   {"name": "중화격", "hanja": "中和格",
                   "description": "오행이 균형잡힌 중화형"},
}


def determine_gyeok_guk(ten_gods_dist: dict) -> dict:
    """
    격국 판단.

    Args:
        ten_gods_dist: calculate_ten_gods_distribution() 결과

    Returns:
        {"type": ..., "name": ..., "hanja": ..., "description": ...}
    """
    total = sum(ten_gods_dist.values())
    derivation: dict
    if total == 0:
        gyeok = "balanced"
        derivation = {"method": "balanced_distribution"}
    else:
        # 특수 종격 판단
        bigeop = ten_gods_dist.get("비견", 0) + ten_gods_dist.get("겁재", 0)
        gwansal = ten_gods_dist.get("정관", 0) + ten_gods_dist.get("편관", 0)
        jaeseong = ten_gods_dist.get("정재", 0) + ten_gods_dist.get("편재", 0)

        if bigeop >= 5 and bigeop / total >= 0.6:
            gyeok = "jong_wang"
            derivation = {"method": "special_jong", "dominant_group": "비겁", "ratio": round(bigeop / total, 2)}
        elif gwansal >= 5 and gwansal / total >= 0.6:
            gyeok = "jong_sal"
            derivation = {"method": "special_jong", "dominant_group": "관살", "ratio": round(gwansal / total, 2)}
        elif jaeseong >= 5 and jaeseong / total >= 0.6:
            gyeok = "jong_jae"
            derivation = {"method": "special_jong", "dominant_group": "재성", "ratio": round(jaeseong / total, 2)}
        else:
            # 가장 많은 십성 → 격국
            dominant = max(ten_gods_dist, key=lambda k: ten_gods_dist[k])
            gyeok = _TEN_GOD_TO_GYEOK.get(dominant, "balanced")
            derivation = {
                "method": "dominant_ten_god",
                "dominant": dominant,
                "note": "전체 십성 분포 최다값 기준 (월지 지장간 투출 우선 적용 없음)",
            }

    info = GYEOK_GUK_INFO[gyeok]
    return {"type": gyeok, **info, "derivation": derivation}
