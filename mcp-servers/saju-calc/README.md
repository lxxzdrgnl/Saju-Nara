# Saju-Calc MCP

사주팔자 **순수 계산 엔진** MCP 서버.

해석 텍스트 없이 4기둥·신살·격국·용신 등 모든 명리 계산 결과를 구조화된 JSON으로 반환합니다.

---

## 설계 원칙

- **계산만, 해석 없음**: 숫자·간지·구조만 반환. 해석 문장은 `saju-rag`가 담당
- **ephem 기반 절기**: 실시간 천문 계산으로 모든 연도 지원
- **korean-lunar-calendar**: 패키지 기반 음양력 변환
- **진태양시 보정**: 한국 실제 경도(127.5°) 기준 -32분 적용

---

## 프로젝트 구조

```
saju-calc/
├── main.py                    # FastMCP 서버 진입점
├── pyproject.toml             # uv 의존성 관리
├── Dockerfile
├── data/
│   ├── heavenly_stems.py      # 천간 10개
│   ├── earthly_branches.py    # 지지 12개 + 지장간 + 삼합/삼형/육해/충/합
│   └── wuxing.py              # 오행 상생/상극
├── lib/
│   ├── solar_terms.py         # ephem 24절기 계산
│   ├── calendar_converter.py  # 음양력 변환
│   ├── saju.py                # 4기둥 계산
│   ├── ten_gods.py            # 십성
│   ├── twelve_wun.py          # 12운성
│   ├── sin_sal.py             # 신살 10종 (Strategy+Registry 패턴)
│   ├── day_master_strength.py # 일간 강약
│   ├── gyeok_guk.py           # 격국 13종
│   ├── yong_sin.py            # 용신
│   ├── dae_un.py              # 대운
│   ├── se_un.py               # 세운·월운·시운 통합
│   ├── compatibility.py       # 궁합
│   ├── structure_patterns.py  # 사주 구조 패턴 감지
│   ├── dynamics.py            # 기둥 간 상호작용 (천간합·통근·지지관계·오행흐름)
│   └── validation.py          # 입력 검증
└── tools/                     # MCP tool 핸들러
    ├── calculate_saju.py
    ├── convert_calendar.py
    ├── get_dae_un.py
    ├── get_un_flow.py
    └── check_compatibility.py
```

---

## 설치 및 실행

### uv (권장)

```bash
# uv 설치 (최초 1회)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 설치
uv sync

# MCP Inspector로 개발 테스트
DANGEROUSLY_OMIT_AUTH=true uv run fastmcp dev inspector main.py
# → http://localhost:6274 접속 후 아래 설정으로 Connect
#   Transport : STDIO
#   Command   : uv
#   Arguments : run python main.py

# 프로덕션 실행
uv run python main.py

# 테스트
uv run pytest tests/

# 개발 의존성 포함 설치
uv sync --group dev
```

### Docker

```bash
# 단일 서비스 실행
docker build -t saju-calc .
docker run -p 8001:8000 saju-calc

# 전체 스택 (루트 디렉토리에서)
docker compose up saju-calc
```

---

## 핵심 계산 공식

### 진태양시 보정
```
실제 사주 계산 시각 = 입력 시각 - 32분
(한국 실제 경도 127.5° 기준. 타 만세력과 결과 차이가 있을 수 있음)
```

### 대운 시작 나이 (만세력 공식)
```
3일 = 1년 (12개월)
1일 = 4개월
→ 절기까지의 일수 × 4 = 대운 시작 개월수
```

### 월주 천간 결정 (연간→월간 규칙)
```
갑·기년 → 인월: 병간 시작
을·경년 → 인월: 무간 시작
병·신년 → 인월: 경간 시작
정·임년 → 인월: 임간 시작
무·계년 → 인월: 갑간 시작
```

---

## 예제 — 이용재 (양력 2001-08-17 자정 00:00, 남성)

### `calculate_saju`

```json
// 입력
{
  "birth_date": "2001-08-17",
  "birth_time": "00:00",
  "gender": "male",
  "calendar": "solar"
}

// 출력
{
  "meta": {
    "time_correction_minutes": -32,
    "applied_time": "2001-08-16T23:28",
    "timezone_note": "UTC+9:00 기준 -32분 보정",
    "gender": "male",
    "birth_date": "2001-08-17",
    "birth_time": "00:00",
    "calendar": "solar",
    "climate_vibe": {
      "season": "autumn",
      "temperature": "cool",
      "humidity": "dry",
      "month_element": "금",
      "day_element_relation": "비(比)"
    }
  },
  "day_master_strength": {
    "level": "very_strong",
    "score": 100,
    "raw_score": 100,
    "score_range": [0, 100],
    "factors": { "wol_ryeong": 40, "bigeop": 5, "inseong": 5, "seolgi": 0 },
    "analysis": "월령을 득하여 강함. 비겁 소량. 인성 소량",
    "wol_ryeong": "strong"
  },
  "yong_sin": {
    "primary": "수", "secondary": "목",
    "xi_sin": ["수", "목"], "ji_sin": ["금", "토"],
    "logic_type": "overpowered_day_master_drain", "reasoning_priority": "억부"
  },
  "gyeok_guk": {
    "type": "geob_jae", "name": "겁재격", "hanja": "劫財格",
    "description": "경쟁심·야망이 강한 도전형",
    "derivation": { "method": "dominant_ten_god", "dominant": "겁재" }
  },
  "year_pillar":  { "stem": "신", "branch": "사", "stem_hanja": "辛", "branch_hanja": "巳", "stem_element": "금", "branch_element": "화", "yin_yang": "음", "stem_ten_god": "비견",  "branch_ten_god": "정관", "twelve_wun": "사"   },
  "month_pillar": { "stem": "병", "branch": "신", "stem_hanja": "丙", "branch_hanja": "申", "stem_element": "화", "branch_element": "금", "yin_yang": "양", "stem_ten_god": "정관", "branch_ten_god": "겁재", "twelve_wun": "병"   },
  "day_pillar":   { "stem": "신", "branch": "해", "stem_hanja": "辛", "branch_hanja": "亥", "stem_element": "금", "branch_element": "수", "yin_yang": "음", "stem_ten_god": "비견",  "branch_ten_god": "상관", "twelve_wun": "목욕" },
  "hour_pillar":  { "stem": "무", "branch": "자", "stem_hanja": "戊", "branch_hanja": "子", "stem_element": "토", "branch_element": "수", "yin_yang": "양", "stem_ten_god": "정인",  "branch_ten_god": "식신", "twelve_wun": "태"   },
  "wuxing_count": { "목": 0.0, "화": 25.0, "토": 12.5, "금": 37.5, "수": 25.0 },
  "dominant_elements": ["금"],
  "weak_elements": ["목"],
  "yin_yang_ratio": { "yang": 50.0, "yin": 50.0 },
  "ten_gods_distribution": {
    "겁재": 30.0, "식신": 10.0, "상관": 10.0, "정관": 30.0, "정인": 20.0
  },
  "ten_gods_void_info": [
    { "category": "재성", "hidden_in_ji_jang_gan": { "day": ["갑"] } }
  ],
  "structure_patterns": [
    { "type": "gwan_in_sang_saeng", "name": "관인상생", "hanja": "官印相生", "desc": "조직(관성)의 지원이 역량(인성)을 키우는 구조 — 승진·제도권 성장에 유리" },
    { "type": "sang_gwan_pae_in",  "name": "상관패인",  "hanja": "傷官佩印", "desc": "상관의 반골 기질을 인성이 다듬는 구조 — 날카로운 직관에 학식을 겸비" }
  ],
  "sin_sals": [
    { "name": "도화살",   "type": "neutral", "priority": "low",  "location": ["day", "hour"],        "desc": "매력과 끼가 넘치며 이성에게 인기가 많음",      "reason": { "trigger": "branch_group", "group_branches": ["해"], "도화지": "자" } },
    { "name": "역마살",   "type": "neutral", "priority": "low",  "location": ["year", "day"],        "desc": "활동적이고 변화를 즐기며 해외·이동 인연이 있음", "reason": { "trigger": "branch_group", "group_branches": ["사"], "역마지": "해" } },
    { "name": "공망",     "type": "unlucky", "priority": "high", "location": ["month"],              "desc": "해당 지지의 기운이 허(虛)하여 그 분야가 약해짐", "reason": { "trigger": "day_branch", "day_branch": "해", "gong_branches": ["신", "유"], "matched_branches": ["신"] } },
    { "name": "원진살",   "type": "unlucky", "priority": "high", "location": ["year", "day"],        "desc": "서로 싫어하고 미워하는 관계 인연이 많음",       "reason": { "trigger": "branch_pair", "pair": ["사", "해"] } },
    { "name": "귀문관살", "type": "unlucky", "priority": "high", "location": ["year", "month", "day"], "desc": "예민한 직관력과 창의적 영감, 신경과민 주의",  "reason": { "trigger": "branch_count", "matched_branches": ["사", "신", "해"], "required_count": 2 } }
  ],
  "branch_relations": {
    "yuk_hap": [{ "pair": ["사", "신"], "element": "수", "is_effective": false, "interference_factors": ["chung", "hae"] }],
    "chung":   [["사", "해"]],
    "yuk_hae": [["신", "해"]],
    "gong_mang": ["신"]
  },
  "ji_jang_gan": {
    "year":  ["병", "무", "경"],
    "month": ["경", "임", "무"],
    "day":   ["임", "갑"],
    "hour":  ["계"]
  },
  "dae_un_start_age": 10,
  "dae_un_list": [
    { "start_age": 10, "end_age": 19, "stem": "을", "branch": "미", "stem_element": "목", "branch_element": "토" },
    { "start_age": 20, "end_age": 29, "stem": "갑", "branch": "오", "stem_element": "목", "branch_element": "화" },
    { "start_age": 30, "end_age": 39, "stem": "계", "branch": "사", "stem_element": "수", "branch_element": "화" },
    { "start_age": 40, "end_age": 49, "stem": "임", "branch": "진", "stem_element": "수", "branch_element": "토" },
    { "start_age": 50, "end_age": 59, "stem": "신", "branch": "묘", "stem_element": "금", "branch_element": "목" },
    { "start_age": 60, "end_age": 69, "stem": "경", "branch": "인", "stem_element": "금", "branch_element": "목" },
    { "start_age": 70, "end_age": 79, "stem": "기", "branch": "축", "stem_element": "토", "branch_element": "토" },
    { "start_age": 80, "end_age": 89, "stem": "무", "branch": "자", "stem_element": "토", "branch_element": "수" }
  ],
  "current_dae_un": {
    "start_age": 20, "end_age": 29,
    "stem": "갑", "branch": "오", "stem_element": "목", "branch_element": "화",
    "stem_ten_god": "정재", "branch_ten_god": "편관"
  },
  "dynamics": {
    "stem_hap": [
      { "type": "stem_hap", "name": "병신합", "pillars": ["year", "month"], "stems": ["신", "병"], "result_element": "수" },
      { "type": "stem_hap", "name": "병신합", "pillars": ["month", "day"],  "stems": ["병", "신"], "result_element": "수" }
    ],
    "rooting_map": {
      "is_rooted": true,
      "pillars": [
        { "pillar": "year",  "via": "ji_jang_gan", "stem": "경", "branch": "사" },
        { "pillar": "month", "via": "branch",                     "branch": "신" }
      ],
      "pillar_count": 2,
      "strength_level": "strong"
    },
    "active_relations": [
      { "type": "yuk_hap", "name": "사신합", "pillars": ["year", "month"], "branches": ["사", "신"], "result_element": "수", "is_effective": false, "interference_factors": ["chung", "hae"] },
      { "type": "chung",   "name": "사해충", "pillars": ["year", "day"],   "branches": ["사", "해"] },
      { "type": "hae",     "name": "신해해", "pillars": ["month", "day"],  "branches": ["신", "해"] }
    ],
    "energy_flow": {
      "generation_chain": ["금", "수"],
      "support_chain": ["화", "토", "금"],
      "is_smooth": true,
      "dominant_flow": "금→수 설기 / 화→토→금 생조 흐름"
    }
  }
}
```

### `get_dae_un`

```json
// 입력
{ "birth_date": "2001-08-17", "birth_time": "00:00", "gender": "male", "count": 8 }

// 출력
[
  { "start_age": 10, "end_age": 19, "stem": "을", "branch": "미", "stem_element": "목", "branch_element": "토" },
  { "start_age": 20, "end_age": 29, "stem": "갑", "branch": "오", "stem_element": "목", "branch_element": "화" },
  { "start_age": 30, "end_age": 39, "stem": "계", "branch": "사", "stem_element": "수", "branch_element": "화" },
  { "start_age": 40, "end_age": 49, "stem": "임", "branch": "진", "stem_element": "수", "branch_element": "토" },
  { "start_age": 50, "end_age": 59, "stem": "신", "branch": "묘", "stem_element": "금", "branch_element": "목" },
  { "start_age": 60, "end_age": 69, "stem": "경", "branch": "인", "stem_element": "금", "branch_element": "목" },
  { "start_age": 70, "end_age": 79, "stem": "기", "branch": "축", "stem_element": "토", "branch_element": "토" },
  { "start_age": 80, "end_age": 89, "stem": "무", "branch": "자", "stem_element": "토", "branch_element": "수" }
]
```

---

## 제공 Tools (5개)

### 1. `calculate_saju`
사주팔자 전체 계산

| 파라미터 | 타입 | 설명 |
|---|---|---|
| `birth_date` | string | 생년월일 `YYYY-MM-DD` |
| `birth_time` | string | 출생 시각 `HH:MM` |
| `gender` | string | `male` \| `female` |
| `calendar` | string | `solar` \| `lunar` (기본값: solar) |
| `is_leap_month` | boolean | 음력 윤달 여부 (기본값: false) |

**반환 필드:**

| 필드 | 설명 |
|---|---|
| `meta` | 계산 기준 + 입력값 echo `{time_correction_minutes, applied_time, timezone_note, gender, ..., climate_vibe}` |
| `meta.climate_vibe` | 조후(調候) `{season, temperature, humidity, month_element, day_element_relation}` — 월지 기후와 일간 관계 (생/설/극/재/비) |
| `day_master_strength` | 일간 강약 `{level, score, raw_score, score_range, factors, analysis, wol_ryeong}` — `raw_score`는 캡 전 원본값 |
| `yong_sin` | 용신 `{primary, secondary, xi_sin, ji_sin, logic_type, reasoning_priority}` |
| `gyeok_guk` | 격국 `{type, name, hanja, description, derivation}` |
| `year/month/day/hour_pillar` | 각 기둥 `{stem, branch, stem_element, branch_element, yin_yang, stem_ten_god, branch_ten_god, twelve_wun}` |
| `wuxing_count` | 오행 분포 % (0.0 포함 — 결핍 오행도 의미 있음, 총합 100) |
| `dominant_elements` / `weak_elements` | 강한/약한 오행 |
| `yin_yang_ratio` | 음양 비율 |
| `ten_gods_distribution` | 십성 분포 % (총합 100) |
| `ten_gods_void_info` | 표면에 없는 십성 그룹 + 지장간 잠재력 대조 `[{category, hidden_in_ji_jang_gan}]` |
| `structure_patterns` | 감지된 사주 구조 패턴 `[{type, name, hanja, desc}]` — 식상생재·관인상생·재다신약·군겁쟁재·식신제살·상관패인·인다신강 |
| `sin_sals` | 신살 10종 `{name, type, priority, desc, location, reason}` |
| `branch_relations` | 합·충·형·해 관계 (키 부재 = 해당 관계 없음). `yuk_hap[].is_effective`: 충·해로 합이 깨지면 false. `interference_factors`: 간섭 유형 목록 |
| `ji_jang_gan` | 지장간 (기둥별 천간 목록) |
| `dae_un_start_age` | 대운 시작 나이 |
| `dae_un_list` | 전체 대운 목록 (10개) |
| `current_dae_un` | 현재 대운 (십성 포함) |
| `dynamics` | 기둥 간 상호작용 분석 (아래 설명 참조) |

**`dynamics` 하위 필드:**

| 필드 | 설명 |
|---|---|
| `stem_hap` | 천간합 목록 `[{type, name, pillars, stems, result_element}]` — 4기둥 천간 간 갑기합·을경합·병신합·정임합·무계합 |
| `rooting_map` | 통근(通根) `{is_rooted, pillars: [{pillar, via, branch, stem?}], pillar_count, strength_level}` — 일간이 어느 기둥에 뿌리를 내렸는지 (`via`: `branch` = 직접 통근, `ji_jang_gan` = 지장간 통근) |
| `active_relations` | 지지 관계 통합 목록 `[{type, name, pillars, branches, ...}]` — 기둥 위치 정보가 포함된 유니파이드 형식. `type`: `sam_hap` \| `yuk_hap` \| `chung` \| `hyung` \| `hae` |
| `energy_flow` | 오행 에너지 흐름 `{generation_chain, support_chain, is_smooth, dominant_flow}` — 일간 중심의 설기·생조 방향 |

---

### 2. `convert_calendar`
양력 ↔ 음력 변환

```json
// 입력
{ "date": "2001-08-17", "from_calendar": "solar", "to_calendar": "lunar" }
// 출력
{ "original_date": "2001-08-17", "converted_date": "2001-06-28", "is_leap_month": false, "solar_term": "입추" }
```

---

### 3. `get_dae_un`
10년 단위 대운 목록

```json
// 입력
{ "birth_date": "2001-08-17", "birth_time": "00:00", "gender": "male", "count": 8 }
// 출력: [{start_age, end_age, stem, branch, stem_element, branch_element}, ...]
```

---

### 4. `get_un_flow`
세운(년) / 월운(월) / 시운 간지 + 일간 관계

```json
// 입력
{ "birth_date": "2001-08-17", "birth_time": "00:00", "gender": "male", "flow_type": "year", "target": "2026" }
// 출력
{ "stem": "병", "branch": "오", "ganji_name": "병오년", "interaction_with_day_master": "...", "interaction_with_yong_sin": "..." }
```

---

### 5. `check_compatibility`
두 사람 궁합 점수 계산

```json
// 입력
{
  "person1": { "birth_date": "2001-08-17", "birth_time": "00:00", "gender": "male" },
  "person2": { "birth_date": "1993-07-22", "birth_time": "09:00", "gender": "female" }
}
// 출력
{ "total_score": 73, "day_pillar_score": 75, "element_harmony_score": 68, ... }
```
