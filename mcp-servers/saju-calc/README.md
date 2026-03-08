# Saju-Calc MCP

사주팔자 **순수 계산 엔진** MCP 서버.

해석 텍스트 없이 4기둥·신살·격국·용신·행동프로파일 등 모든 명리 계산 결과를 구조화된 JSON으로 반환합니다.

---

## 설계 원칙

- **계산만, 해석 없음**: 숫자·간지·구조만 반환. 해석 문장은 saju-rag가 담당
- **12단계 파이프라인**: 4기둥 → 십성 → 신살 → 격국 → 용신 → 패턴 → 시너지 → 행동합성 → 랭킹 → 도메인
- **ephem 절기**: 실시간 천문 계산으로 모든 연도 지원 (하드코딩 테이블 없음)
- **진태양시 보정**: 한국 실제 경도(127.5°) 기준 -32분 적용

---

## 프로젝트 구조

```
saju-calc/
├── main.py                        # FastMCP 서버 진입점
├── pyproject.toml
├── data/
│   ├── heavenly_stems.py          # 천간 10개
│   ├── earthly_branches.py        # 지지 12개 + 지장간 + 삼합/삼형/육해/충/합
│   ├── wuxing.py                  # 오행 상생/상극
│   └── timezone_history.py        # 한국 역사적 시간대 보정
├── lib/
│   ├── saju.py                    # 4기둥 계산 (연·월·일·시주)
│   ├── solar_terms.py             # ephem 24절기 계산
│   ├── calendar_converter.py      # 음양력 변환
│   ├── ten_gods.py                # 십성 계산
│   ├── twelve_wun.py              # 12운성
│   ├── sin_sal.py                 # 신살 10종 (Strategy+Registry 패턴)
│   ├── day_master_strength.py     # 일간 강약 점수화
│   ├── gyeok_guk.py               # 격국 13종
│   ├── yong_sin.py                # 용신 (억부·조후·통관)
│   ├── dae_un.py                  # 대운 (절기 기반 3일=1년)
│   ├── se_un.py                   # 세운·월운·시운
│   ├── compatibility.py           # 궁합 점수
│   ├── structure_patterns.py      # 구조 패턴 15종 (PatternRegistry v2.4)
│   ├── dynamics.py                # 기둥 간 상호작용 (천간합·통근·지지관계·오행흐름)
│   ├── synergy.py                 # 패턴 × 동역학 교차 시너지 (30규칙)
│   ├── behavior_synthesizer.py    # 십성 분포 → behavior_profile 합성
│   ├── context_ranker.py          # 패턴·신살 우선순위화 → primary/secondary
│   ├── life_domain_mapper.py      # 도메인별 태그 분류 (career·relationship·wealth·personality)
│   └── validation.py              # 입력 검증
└── tools/
    ├── calculate_saju.py          # tool 핸들러
    ├── convert_calendar.py
    ├── get_dae_un.py
    ├── get_un_flow.py
    └── check_compatibility.py
```

---

## 설치 및 실행

```bash
# uv 설치 (최초 1회)
curl -LsSf https://astral.sh/uv/install.sh | sh

cd mcp-servers/saju-calc

# 의존성 설치
uv sync --group dev

# MCP Inspector (개발 테스트)
DANGEROUSLY_OMIT_AUTH=true uv run fastmcp dev inspector main.py
# → http://localhost:6274
#   Transport: STDIO  /  Command: uv  /  Arguments: run python main.py

# 프로덕션 실행
uv run python main.py

# 테스트
uv run pytest tests/
```

```bash
# Docker
docker build -t saju-calc .
docker run -p 8001:8000 saju-calc

# 전체 스택 (루트에서)
docker compose up saju-calc
```

---

## 핵심 계산 공식

### 진태양시 보정
```
보정 시각 = 입력 시각 - 32분
(한국 실제 경도 127.5° 기준. 1961년 이전은 역사적 시간대 별도 처리)
```

### 대운 시작 나이
```
절기까지 일수 × 4개월 = 대운 시작 개월수
(3일 = 1년, 1일 = 4개월)
```

### 월주 천간 결정
```
갑·기년 → 인월: 병간 시작
을·경년 → 인월: 무간 시작
병·신년 → 인월: 경간 시작
정·임년 → 인월: 임간 시작
무·계년 → 인월: 갑간 시작
```

---

## Calc 내부 파이프라인 (calculate_saju 기준)

```
① 4기둥           진태양시 보정 → 연·월·일·시주 간지
② 십성 + 12운성   기둥별 십성(천간·지지) + 12운성
③ 신살            역마·도화·귀문관살 등 10종 + priority 태그
④ 일간 강약       월령·비겁·인성·설기 점수화 (very_weak~very_strong)
⑤ 격국            월령 + 십성 분포 → 13종 판별
⑥ 용신            억부 / 조후 / 통관 로직 선택
⑦ 대운            10년 단위 대운 목록 + 현재 대운
⑧ 음양 비율       8글자(천간4 + 지지4) 기준
⑨ 구조 패턴       15종 (종격3 + exclusive_group 억제)
   동역학          천간합·통근·지지관계·오행흐름
   시너지          (패턴id, dynamics_key) → synergy_tags (30규칙)
⑩ 행동 프로파일   십성% × 위치가중치 → behavior_vector 점수 합산 → top 6
⑪ 컨텍스트 랭킹   패턴·신살 priority + rarity + interaction → primary 3 / secondary 2
⑫ 생활 도메인     behavior_vector + context_ranking → career·relationship·wealth·personality
```

---

## 제공 Tools (5개)

### 1. `calculate_saju`

| 파라미터 | 타입 | 설명 |
|---|---|---|
| `birth_date` | string | `YYYY-MM-DD` |
| `birth_time` | string | `HH:MM` |
| `gender` | string | `male` \| `female` |
| `calendar` | string | `solar` \| `lunar` (기본: solar) |
| `is_leap_month` | boolean | 음력 윤달 여부 (기본: false) |

**반환 구조 (12그룹):**

| 그룹 | 필드 | 설명 |
|---|---|---|
| ① meta | `meta` | 계산 기준·입력값·조후(climate_vibe) |
| ② 핵심 | `day_master_strength` | 일간 강약 level·score·factors |
| | `yong_sin` | 용신 primary·secondary·logic_type |
| | `gyeok_guk` | 격국 type·name·hanja·derivation |
| ③ 4기둥 | `year/month/day/hour_pillar` | stem·branch·십성·12운성 |
| ④ 분포 | `wuxing_count` | 오행 % (0.0 포함) |
| | `yin_yang_ratio` | 음양 비율 % |
| ⑤ 십성 | `ten_gods_distribution` | 십성 % (총합 100) |
| | `ten_gods_void_info` | 결핍 카테고리 + 지장간 잠재력 |
| ⑥ 구조 | `structure_patterns` | 감지된 패턴 목록 |
| | `sin_sals` | 신살 10종 + priority + reason |
| | `branch_relations` | 합·충·형·해 (yuk_hap에 is_effective 포함) |
| | `ji_jang_gan` | 기둥별 지장간 |
| ⑦ 대운 | `dae_un_list` | 10개 대운 목록 |
| | `current_dae_un` | 현재 대운 + 십성 |
| ⑧ 동역학 | `dynamics` | stem_hap·rooting_map·active_relations·energy_flow |
| ⑨ 시너지 | `synergy` | [{pattern_id, dynamics_key, synergy_tags}] |
| ⑩ 행동 | `behavior_profile` | top 6 behavior_tag (RAG 쿼리 seed) |
| ⑪ 랭킹 | `context_ranking` | primary 3 + secondary 2 컨텍스트 |
| ⑫ 도메인 | `life_domains` | career·relationship·wealth·personality 태그 |

---

### 2. `convert_calendar`

```json
{ "date": "2001-08-17", "from_calendar": "solar", "to_calendar": "lunar" }
→ { "original_date": "2001-08-17", "converted_date": "2001-06-28", "is_leap_month": false, "solar_term": "입추" }
```

### 3. `get_dae_un`

```json
{ "birth_date": "2001-08-17", "birth_time": "00:00", "gender": "male", "count": 8 }
→ [{ "start_age": 10, "end_age": 19, "stem": "을", "branch": "미", ... }, ...]
```

### 4. `get_un_flow`

```json
{ "birth_date": "2001-08-17", "birth_time": "00:00", "gender": "male", "flow_type": "year", "target": "2026" }
→ { "stem": "병", "branch": "오", "ganji_name": "병오년", "interaction_with_day_master": "..." }
```

### 5. `check_compatibility`

```json
{
  "person1": { "birth_date": "2001-08-17", "birth_time": "00:00", "gender": "male" },
  "person2": { "birth_date": "1993-07-22", "birth_time": "09:00", "gender": "female" }
}
→ { "total_score": 73, "day_pillar_score": 75, "element_harmony_score": 68, ... }
```

---

## 예제 출력 — 이용재 (2001-08-17 00:00, 남성, 양력)

```json
{
  "meta": {
    "time_correction_minutes": -32,
    "applied_time": "2001-08-16T23:28",
    "climate_vibe": { "season": "autumn", "temperature": "cool", "humidity": "dry", "month_element": "금", "day_element_relation": "비(比)" }
  },
  "day_master_strength": { "level": "very_strong", "score": 100 },
  "yong_sin": { "primary": "수", "secondary": "목", "logic_type": "overpowered_day_master_drain" },
  "gyeok_guk": { "type": "geob_jae", "name": "겁재격" },
  "year_pillar":  { "stem": "신", "branch": "사", "stem_ten_god": "비견",  "branch_ten_god": "정관", "twelve_wun": "사"   },
  "month_pillar": { "stem": "병", "branch": "신", "stem_ten_god": "정관", "branch_ten_god": "겁재", "twelve_wun": "병"   },
  "day_pillar":   { "stem": "신", "branch": "해", "stem_ten_god": "비견",  "branch_ten_god": "상관", "twelve_wun": "목욕" },
  "hour_pillar":  { "stem": "무", "branch": "자", "stem_ten_god": "정인",  "branch_ten_god": "식신", "twelve_wun": "태"   },
  "wuxing_count": { "목": 0.0, "화": 25.0, "토": 12.5, "금": 37.5, "수": 25.0 },
  "ten_gods_distribution": { "겁재": 30.0, "식신": 10.0, "상관": 10.0, "정관": 30.0, "정인": 20.0 },
  "structure_patterns": [
    { "id": "gwan_in_sang_saeng", "name": "관인상생", "priority": 70 },
    { "id": "sang_gwan_pae_in",  "name": "상관패인",  "priority": 60 }
  ],
  "dynamics": {
    "stem_hap": [{ "name": "병신합", "pillars": ["year", "month"], "result_element": "수" }],
    "rooting_map": { "strength_level": "strong", "pillar_count": 2 },
    "energy_flow": { "is_smooth": true, "dominant_flow": "금→수 설기 / 화→토→금 생조" }
  },
  "synergy": [
    { "pattern_id": "sang_gwan_pae_in", "dynamics_key": "stem_hap:병신합", "synergy_tags": ["analytical_humor_defense", "calculated_resilience"] }
  ],
  "behavior_profile": ["rule_adherence", "competitive_drive", "scholarly_pursuit", "sharp_expression", "self_reliance", "creative_expression"],
  "context_ranking": {
    "primary_context":   [{ "id": "gwan_in_sang_saeng", "type": "pattern", "score": 70.0 }, { "id": "귀문관살", "type": "sin_sal", "score": 75.0 }],
    "secondary_context": [{ "id": "sang_gwan_pae_in",   "type": "pattern", "score": 60.0 }]
  },
  "life_domains": {
    "career":       ["rule_adherence", "institutional_growth", "sharp_expression"],
    "relationship": ["responsibility_acceptance", "sharp_expression"],
    "wealth":       ["credential_income", "creative_expression"],
    "personality":  ["scholarly_pursuit", "self_reliance", "competitive_drive"]
  }
}
```
