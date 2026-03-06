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

## 예제 — 이용재 (양력 2001-08-17 오전 11시, 남성)

### `calculate_saju`

```json
// 입력
{
  "birth_date": "2001-08-17",
  "birth_time": "11:00",
  "gender": "male",
  "calendar": "solar"
}

// 출력
{
  "year_pillar":  { "stem": "신", "branch": "사", "stem_hanja": "辛", "branch_hanja": "巳", "stem_element": "금", "branch_element": "화", "yin_yang": "음", "stem_ten_god": "정인",  "branch_ten_god": "편재", "twelve_wun": "사"   },
  "month_pillar": { "stem": "병", "branch": "신", "stem_hanja": "丙", "branch_hanja": "申", "stem_element": "화", "branch_element": "금", "yin_yang": "양", "stem_ten_god": "편재",  "branch_ten_god": "편인", "twelve_wun": "병"   },
  "day_pillar":   { "stem": "임", "branch": "자", "stem_hanja": "壬", "branch_hanja": "子", "stem_element": "수", "branch_element": "수", "yin_yang": "양", "stem_ten_god": "비견",  "branch_ten_god": "겁재", "twelve_wun": "제왕" },
  "hour_pillar":  { "stem": "을", "branch": "사", "stem_hanja": "乙", "branch_hanja": "巳", "stem_element": "목", "branch_element": "화", "yin_yang": "음", "stem_ten_god": "상관",  "branch_ten_god": "편재", "twelve_wun": "목욕" },
  "wuxing_count": { "목": 1, "화": 3, "토": 0, "금": 2, "수": 2 },
  "dominant_elements": ["화"],
  "weak_elements": ["토"],
  "yin_yang_ratio": { "yang": 50.0, "yin": 50.0 },
  "ten_gods_distribution": {
    "비견": 0.0, "겁재": 0.5, "식신": 0.0, "상관": 1.0,
    "편재": 2.0, "정재": 0.0, "편관": 0.0, "정관": 0.0,
    "편인": 0.5, "정인": 1.0
  },
  "branch_relations": {
    "sam_hap": null,
    "yuk_hap": [{ "pair": ["사", "신"], "element": "수" }],
    "chung": [],
    "sam_hyeong": [],
    "yuk_hae": [],
    "gong_mang": []
  },
  "ji_jang_gan": {
    "year":  ["병", "무", "경"],
    "month": ["경", "임", "무"],
    "day":   ["계"],
    "hour":  ["병", "무", "경"]
  },
  "sin_sals": [
    {
      "name": "천을귀인", "type": "lucky", "priority": "medium",
      "desc": "인복이 많고 위기에서 귀인의 도움을 받음",
      "reason": { "trigger": "day_stem", "day_stem": "임", "matched_branches": ["사"] }
    },
    {
      "name": "귀문관살", "type": "unlucky", "priority": "high",
      "desc": "예민한 직관력과 창의적 영감, 신경과민 주의",
      "reason": { "trigger": "branch_count", "matched_branches": ["사", "신"], "required_count": 2 }
    },
    {
      "name": "양인살", "type": "unlucky", "priority": "high",
      "desc": "강한 추진력과 승부욕, 다혈질적 기질",
      "reason": { "trigger": "day_stem", "day_stem": "임", "yang_in_branch": "자" }
    }
  ],
  "day_master_strength": {
    "level": "very_strong", "score": 85,
    "analysis": "월령을 득하여 강함. 비겁 없음. 인성 소량",
    "wol_ryeong": "strong"
  },
  "gyeok_guk": {
    "type": "pyeon_jae", "name": "편재격", "hanja": "偏財格",
    "description": "사교적이고 사업 수완이 뛰어난 활동형"
  },
  "yong_sin": {
    "primary": "목", "secondary": "화",
    "xi_sin": ["목", "화"], "ji_sin": ["수", "금"],
    "reasoning": "일간(수)이 강하므로 설기하는 목(식상)·화(재성)을 용신으로 삼음"
  },
  "dae_un_start_age": 4,
  "current_dae_un": {
    "start_age": 24, "end_age": 33,
    "stem": "계", "branch": "사",
    "stem_element": "수", "branch_element": "화",
    "stem_ten_god": "겁재", "branch_ten_god": "편재"
  },
  "meta": {
    "time_correction_minutes": -32,
    "applied_time": "2001-08-17T10:28",
    "timezone_note": "UTC+9:00 기준 -32분 보정"
  }
}
```

### `get_dae_un`

```json
// 입력
{ "birth_date": "2001-08-17", "birth_time": "11:00", "gender": "male", "count": 8 }

// 출력
[
  { "start_age":  4, "end_age": 13, "stem": "을", "branch": "미", "stem_element": "목", "branch_element": "토" },
  { "start_age": 14, "end_age": 23, "stem": "갑", "branch": "오", "stem_element": "목", "branch_element": "화" },
  { "start_age": 24, "end_age": 33, "stem": "계", "branch": "사", "stem_element": "수", "branch_element": "화" },
  { "start_age": 34, "end_age": 43, "stem": "임", "branch": "진", "stem_element": "수", "branch_element": "토" },
  { "start_age": 44, "end_age": 53, "stem": "신", "branch": "묘", "stem_element": "금", "branch_element": "목" },
  { "start_age": 54, "end_age": 63, "stem": "경", "branch": "인", "stem_element": "금", "branch_element": "목" },
  { "start_age": 64, "end_age": 73, "stem": "기", "branch": "축", "stem_element": "토", "branch_element": "토" },
  { "start_age": 74, "end_age": 83, "stem": "무", "branch": "자", "stem_element": "토", "branch_element": "수" }
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
| `year/month/day/hour_pillar` | 각 기둥 (stem, branch, 십성, 12운성 포함) |
| `wuxing_count` | 오행 개수 |
| `dominant_elements` / `weak_elements` | 강한/약한 오행 |
| `yin_yang_ratio` | 음양 비율 `{yang: 50.0, yin: 50.0}` |
| `sin_sals` | 신살 10종 `{name, type, priority, desc, reason}` — `reason`은 트리거 데이터 구조체 |
| `branch_relations` | 합·충·형·파·해 관계 |
| `ji_jang_gan` | 지장간 |
| `day_master_strength` | 일간 강약 `{level, score, analysis}` |
| `gyeok_guk` | 격국 |
| `yong_sin` | 용신 `{primary, secondary, xi_sin, ji_sin}` |
| `dae_un_start_age` | 대운 시작 나이 |
| `current_dae_un` | 현재 대운 (십성 포함) |
| `meta` | 시간 보정 기준 명시 |

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
{ "birth_date": "2001-08-17", "birth_time": "11:00", "gender": "male", "count": 8 }
// 출력: [{start_age, end_age, stem, branch, stem_element, branch_element}, ...]
```

---

### 4. `get_un_flow`
세운(년) / 월운(월) / 시운 간지 + 일간 관계

```json
// 입력
{ "birth_date": "2001-08-17", "birth_time": "11:00", "gender": "male", "flow_type": "year", "target": "2026" }
// 출력
{ "stem": "병", "branch": "오", "ganji_name": "병오년", "interaction_with_day_master": "...", "interaction_with_yong_sin": "..." }
```

---

### 5. `check_compatibility`
두 사람 궁합 점수 계산

```json
// 입력
{
  "person1": { "birth_date": "2001-08-17", "birth_time": "11:00", "gender": "male" },
  "person2": { "birth_date": "1993-07-22", "birth_time": "09:00", "gender": "female" }
}
// 출력
{ "total_score": 73, "day_pillar_score": 75, "element_harmony_score": 68, ... }
```
