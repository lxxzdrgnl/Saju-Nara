"""
동역학(Dynamics) — 기둥 간 상호작용 분석.

1. stem_hap      : 천간합(天干合) — 4기둥 천간 간 합화
2. rooting_map   : 통근(通根) — 일간이 어느 기둥 지지에 뿌리를 내리는지
3. active_relations : 지지 관계(支支關係)를 기둥 위치 정보로 재포맷
4. energy_flow   : 오행 생극 흐름 (일간 중심)

Writer Agent가 "재료(재료 데이터)"를 "레시피(관계도)"로 활용할 수 있도록
기둥 간 연결 정보를 구조화된 형태로 제공한다.
"""

from __future__ import annotations
from data.earthly_branches import SAM_HYEONG

# ─── 정적 테이블 ────────────────────────────────────────────────

# 천간 → 오행
_STEM_ELEMENT: dict[str, str] = {
    "갑": "목", "을": "목",
    "병": "화", "정": "화",
    "무": "토", "기": "토",
    "경": "금", "신": "금",
    "임": "수", "계": "수",
}

# 천간합 (쌍, 이름, 합화 오행)
_STEM_HAP_TABLE: list[tuple[frozenset, str, str]] = [
    (frozenset({"갑", "기"}), "갑기합", "토"),
    (frozenset({"을", "경"}), "을경합", "금"),
    (frozenset({"병", "신"}), "병신합", "수"),
    (frozenset({"정", "임"}), "정임합", "목"),
    (frozenset({"무", "계"}), "무계합", "화"),
]

# 오행 상생 순환
_WUXING_GEN: dict[str, str] = {
    "목": "화", "화": "토", "토": "금", "금": "수", "수": "목",
}

# 오행 상극 순환
_WUXING_DEST: dict[str, str] = {
    "목": "토", "토": "수", "수": "화", "화": "금", "금": "목",
}

_PILLAR_LABELS = ["year", "month", "day", "hour"]
_PILLAR_KEYS   = ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]


# ─── 1. 천간합 ──────────────────────────────────────────────────

def _calc_stem_hap(saju: dict) -> list[dict]:
    """천간합 — 4기둥 천간 간 합화 검사."""
    stems = {
        label: saju[key]["stem"]
        for label, key in zip(_PILLAR_LABELS, _PILLAR_KEYS)
    }
    results = []
    pairs = [
        (l1, l2)
        for i, l1 in enumerate(_PILLAR_LABELS)
        for l2 in _PILLAR_LABELS[i + 1:]
    ]
    for l1, l2 in pairs:
        s1, s2 = stems[l1], stems[l2]
        for pair_set, name, result_el in _STEM_HAP_TABLE:
            if frozenset({s1, s2}) == pair_set:
                results.append({
                    "type": "stem_hap",
                    "name": name,
                    "pillars": [l1, l2],
                    "stems": [s1, s2],
                    "result_element": result_el,
                })
    return results


# ─── 2. 통근맵 ─────────────────────────────────────────────────

def _calc_rooting_map(saju: dict) -> dict:
    """통근맵 — 일간이 어느 기둥 지지에 뿌리를 내리는지.

    통근 판정:
    - 직접 통근: 지지 오행 == 일간 오행
    - 지장간 통근: 지장간 천간 중 일간 오행과 같은 것 존재
    """
    day_element = saju["day_pillar"]["stem_element"]
    ji_jang_gan: dict[str, list[str]] = saju["ji_jang_gan"]
    rooted: list[dict] = []

    for label, key in zip(_PILLAR_LABELS, _PILLAR_KEYS):
        branch = saju[key]["branch"]
        branch_el = saju[key]["branch_element"]

        if branch_el == day_element:
            rooted.append({"pillar": label, "via": "branch", "branch": branch})
            continue

        for stem in ji_jang_gan.get(label, []):
            if _STEM_ELEMENT.get(stem) == day_element:
                rooted.append({
                    "pillar": label,
                    "via": "ji_jang_gan",
                    "stem": stem,
                    "branch": branch,
                })
                break

    count = len(rooted)
    if count >= 3:
        strength_level = "very_strong"
    elif count == 2:
        strength_level = "strong"
    elif count == 1:
        strength_level = "moderate"
    else:
        strength_level = "none"

    return {
        "is_rooted": count > 0,
        "pillars": rooted,
        "pillar_count": count,
        "strength_level": strength_level,
    }


# ─── 3. active_relations ────────────────────────────────────────

def _branch_to_pillar_map(saju: dict) -> dict[str, list[str]]:
    """지지 → 기둥 레이블 매핑 (중복 지지 허용)."""
    result: dict[str, list[str]] = {}
    for label, key in zip(_PILLAR_LABELS, _PILLAR_KEYS):
        b = saju[key]["branch"]
        result.setdefault(b, []).append(label)
    return result


def _branches_to_pillars(
    branches: list[str] | tuple[str, ...],
    b2p: dict[str, list[str]],
) -> list[str]:
    """지지 목록 → 기둥 레이블 목록 (순서 유지)."""
    seen: set[str] = set()
    result: list[str] = []
    for b in branches:
        for p in b2p.get(b, []):
            if p not in seen:
                seen.add(p)
                result.append(p)
    return sorted(result, key=lambda x: _PILLAR_LABELS.index(x))


def _calc_active_relations(saju: dict, branch_relations: dict) -> list[dict]:
    """지지 관계를 기둥 위치 정보가 포함된 unified 리스트로 변환."""
    b2p = _branch_to_pillar_map(saju)
    results: list[dict] = []

    # 삼합
    sam_hap = branch_relations.get("sam_hap")
    if sam_hap:
        branches = sam_hap["branches"]
        results.append({
            "type": "sam_hap",
            "name": sam_hap["name"],
            "pillars": _branches_to_pillars(branches, b2p),
            "branches": branches,
            "result_element": sam_hap["element"],
        })

    # 육합 (is_effective 포함)
    for h in branch_relations.get("yuk_hap", []):
        pair = list(h["pair"])
        entry: dict = {
            "type": "yuk_hap",
            "name": f"{''.join(pair)}합",
            "pillars": _branches_to_pillars(pair, b2p),
            "branches": pair,
            "result_element": h["element"],
        }
        if "is_effective" in h:
            entry["is_effective"] = h["is_effective"]
            entry["interference_factors"] = h.get("interference_factors", [])
        results.append(entry)

    # 충
    for pair in branch_relations.get("chung", []):
        results.append({
            "type": "chung",
            "name": f"{''.join(pair)}충",
            "pillars": _branches_to_pillars(pair, b2p),
            "branches": list(pair),
        })

    # 삼형 — check_sam_hyeong는 이름 문자열 목록 반환; SAM_HYEONG로 지지 역조회
    for hyung_name in branch_relations.get("sam_hyeong", []):
        branches = SAM_HYEONG.get(hyung_name, [])
        results.append({
            "type": "hyung",
            "name": hyung_name,
            "pillars": _branches_to_pillars(branches, b2p),
            "branches": branches,
        })

    # 육해
    for pair in branch_relations.get("yuk_hae", []):
        results.append({
            "type": "hae",
            "name": f"{''.join(pair)}해",
            "pillars": _branches_to_pillars(pair, b2p),
            "branches": list(pair),
        })

    return results


# ─── 4. energy_flow ─────────────────────────────────────────────

def _calc_energy_flow(saju: dict, wuxing_pct: dict[str, float]) -> dict:
    """오행 생극 흐름 — 일간 중심의 에너지 흐름을 구조화.

    - generation_chain : 일간 → 설기 방향으로 연결되는 오행 체인
    - support_chain    : 생조 방향 (일간을 강화하는 오행 경로)
    - dominant_flow    : 가장 두드러진 흐름 설명
    """
    day_el = saju["day_pillar"]["stem_element"]
    present = {el for el, pct in wuxing_pct.items() if pct > 0}

    # 일간에서 설기 방향 체인 (최대 3단계)
    gen_chain = [day_el]
    cur = day_el
    for _ in range(3):
        nxt = _WUXING_GEN.get(cur)
        if nxt and nxt in present and nxt != day_el:
            gen_chain.append(nxt)
            cur = nxt
        else:
            break

    # 일간을 생하는 방향 체인 (최대 2단계)
    gen_reverse: dict[str, str] = {v: k for k, v in _WUXING_GEN.items()}
    sup_chain = []
    cur = day_el
    for _ in range(2):
        prev = gen_reverse.get(cur)
        if prev and prev in present and prev != day_el:
            sup_chain.insert(0, prev)
            cur = prev
        else:
            break

    # 흐름 원활성: 생극 관계만 존재하고 역관계 없으면 smooth
    conflict_el = _WUXING_DEST.get(day_el)
    is_smooth = conflict_el not in present or wuxing_pct.get(conflict_el, 0) < 20

    # 흐름 이름
    flow_labels: list[str] = []
    if len(gen_chain) >= 3:
        flow_labels.append(f"{'→'.join(gen_chain)} 설기 흐름")
    elif len(gen_chain) == 2:
        flow_labels.append(f"{day_el}→{gen_chain[1]} 설기")
    if sup_chain:
        flow_labels.append(f"{'→'.join(sup_chain + [day_el])} 생조 흐름")

    return {
        "generation_chain": gen_chain,    # 일간→설기 방향
        "support_chain": sup_chain + [day_el] if sup_chain else [day_el],  # 생조→일간
        "is_smooth": is_smooth,
        "dominant_flow": " / ".join(flow_labels) if flow_labels else f"{day_el} 독립",
    }


# ─── 공개 API ───────────────────────────────────────────────────

def build_dynamics(
    saju: dict,
    branch_relations: dict,
    wuxing_pct: dict[str, float],
) -> dict:
    """
    동역학 분석 통합 빌더.

    Args:
        saju           : calculate_saju()의 원본 결과 (4기둥 + ji_jang_gan 포함)
        branch_relations : calculate_saju.py에서 필터링된 branch_rel
        wuxing_pct     : 오행 퍼센트 분포 (calculate_saju.py에서 계산된 값)

    Returns:
        stem_hap         : 천간합 목록
        rooting_map      : 통근 정보
        active_relations : 지지 관계 + 기둥 위치 통합 목록
        energy_flow      : 오행 에너지 흐름
    """
    return {
        "stem_hap": _calc_stem_hap(saju),
        "rooting_map": _calc_rooting_map(saju),
        "active_relations": _calc_active_relations(saju, branch_relations),
        "energy_flow": _calc_energy_flow(saju, wuxing_pct),
    }
