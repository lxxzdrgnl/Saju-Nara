"""
작명(作名) 오행 분석 — 한글 초성 → 오행 매핑.
"""

from __future__ import annotations

# 한글 자음 → 오행 (전통 음오행론)
_CONSONANT_WUXING: dict[str, str] = {
    "ㄱ": "목", "ㅋ": "목",
    "ㄴ": "화", "ㄷ": "화", "ㄹ": "화", "ㅌ": "화",
    "ㅇ": "토", "ㅎ": "토",
    "ㅅ": "금", "ㅈ": "금", "ㅊ": "금",
    "ㅁ": "수", "ㅂ": "수", "ㅍ": "수",
}


def _extract_initial(char: str) -> str | None:
    """한글 글자에서 초성(자음) 추출."""
    code = ord(char) - 0xAC00
    if code < 0 or code > 11171:
        return None
    initial_idx = code // (21 * 28)
    initials = [
        "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ",
        "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ",
    ]
    return initials[initial_idx]


def analyze_name(name: str, yong_sin: str | None = None) -> dict:
    """
    한글 이름 오행 분석.

    Args:
        name:     한글 이름 (예: "김민준")
        yong_sin: 용신 오행 (적합도 계산용, 없으면 None)

    Returns:
        characters, element_distribution, yong_sin_match_score, missing_yong_sin
    """
    characters = []
    dist: dict[str, int] = {"목": 0, "화": 0, "토": 0, "금": 0, "수": 0}

    for char in name:
        initial = _extract_initial(char)
        if initial is None:
            continue
        # 쌍자음·이중자음은 기본 자음으로 정규화
        base = initial.replace("ㄲ", "ㄱ").replace("ㄸ", "ㄷ").replace("ㅃ", "ㅂ") \
                      .replace("ㅆ", "ㅅ").replace("ㅉ", "ㅈ")
        element = _CONSONANT_WUXING.get(base)
        characters.append({
            "char": char,
            "consonant": initial,
            "element": element,
        })
        if element:
            dist[element] += 1

    # 용신 적합도
    yong_sin_match_score = None
    missing_yong_sin = None
    if yong_sin:
        total = sum(dist.values()) or 1
        match = dist.get(yong_sin, 0)
        yong_sin_match_score = int(match / total * 100)
        missing_yong_sin = match == 0

    return {
        "name": name,
        "characters": characters,
        "element_distribution": dist,
        "yong_sin_match_score": yong_sin_match_score,
        "missing_yong_sin": missing_yong_sin,
    }
