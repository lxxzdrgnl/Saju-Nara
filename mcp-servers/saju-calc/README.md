# Saju-Calc MCP

사주팔자 **순수 계산 엔진** MCP 서버.

해석 텍스트 없이 4기둥·신살·격국·용신 등 모든 명리 계산 결과를 구조화된 JSON으로 반환합니다.

---

## 설계 원칙

- **계산만, 해석 없음**: 숫자·간지·구조만 반환. 해석 문장은 `saju-rag`가 담당
- **ephem 기반 절기**: 실시간 천문 계산으로 모든 연도 지원
- **korean-lunar-calendar**: 패키지 기반 음양력 변환

---

## 프로젝트 구조

```
saju-calc/
├── main.py                  # FastMCP 서버 진입점
├── pyproject.toml           # uv 의존성 관리
├── Dockerfile
├── data/
│   ├── heavenly_stems.py    # 천간 10개
│   ├── earthly_branches.py  # 지지 12개 + 지장간 + 삼합/삼형/육해/충/합
│   └── wuxing.py            # 오행 상생/상극
├── lib/
│   ├── solar_terms.py       # ephem 24절기 계산
│   ├── calendar_converter.py
│   ├── saju.py              # 4기둥 계산
│   ├── ten_gods.py
│   ├── sin_sal.py
│   ├── day_master_strength.py
│   ├── gyeok_guk.py
│   ├── yong_sin.py
│   ├── dae_un.py
│   ├── se_un.py              # 세운·월운·시운 통합
│   ├── compatibility.py
│   ├── jakmeong.py
│   └── validation.py
└── tools/                   # MCP tool 핸들러
    ├── calculate_saju.py
    ├── convert_calendar.py
    ├── get_dae_un.py
    ├── get_un_flow.py
    ├── check_compatibility.py
    └── analyze_name.py
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
실제 사주 계산 시각 = 입력 시각 - 30분
(한국 KST는 UTC+9이나 실제 천문시와 약 30분 차이)
```

### 대운 시작 나이 (만세력 공식)
```
3일 = 1년 (12개월)
1일 = 4개월
1시진(2시간) = 10일 = 40개월
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
  "year_pillar":  { "stem": "신", "branch": "사", "stem_element": "금", "branch_element": "화", "yin_yang": "음", "stem_ten_god": "정인",  "branch_ten_god": "편재" },
  "month_pillar": { "stem": "병", "branch": "신", "stem_element": "화", "branch_element": "금", "yin_yang": "양", "stem_ten_god": "편재",  "branch_ten_god": "편인" },
  "day_pillar":   { "stem": "임", "branch": "자", "stem_element": "수", "branch_element": "수", "yin_yang": "양", "stem_ten_god": "비견",  "branch_ten_god": "겁재" },
  "hour_pillar":  { "stem": "을", "branch": "사", "stem_element": "목", "branch_element": "화", "yin_yang": "음", "stem_ten_god": "상관",  "branch_ten_god": "편재" },
  "wuxing_count": { "목": 1, "화": 3, "토": 0, "금": 2, "수": 2 },
  "dominant_elements": ["화"],
  "weak_elements": ["토"],
  "sin_sals": [
    { "name": "천을귀인", "type": "lucky",   "desc": "인복이 많고 위기에서 귀인의 도움을 받음" },
    { "name": "귀문관살", "type": "unlucky", "desc": "예민한 직관력과 창의적 영감, 신경과민 주의" },
    { "name": "양인살",   "type": "unlucky", "desc": "강한 추진력과 승부욕, 다혈질적 기질" }
  ],
  "day_master_strength": { "level": "very_strong", "score": 85, "analysis": "월령을 득하여 강함. 비겁 없음. 인성 소량" },
  "gyeok_guk": { "name": "편재격", "hanja": "偏財格", "description": "사교적이고 사업 수완이 뛰어난 활동형" },
  "yong_sin": { "primary": "목", "secondary": "화", "xi_sin": ["목", "화"], "ji_sin": ["수", "금"] },
  "dae_un_start_age": 4,
  "current_dae_un": { "start_age": 24, "end_age": 33, "stem": "계", "branch": "사", "stem_ten_god": "겁재", "branch_ten_god": "편재" }
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

### `analyze_name`

```json
// 입력
{ "name": "이용재", "birth_date": "2001-08-17", "birth_time": "11:00", "gender": "male" }

// 출력
{
  "name": "이용재",
  "characters": [
    { "char": "이", "consonant": "ㅇ", "element": "토" },
    { "char": "용", "consonant": "ㅇ", "element": "토" },
    { "char": "재", "consonant": "ㅈ", "element": "금" }
  ],
  "element_distribution": { "목": 0, "화": 0, "토": 2, "금": 1, "수": 0 },
  "yong_sin_match_score": 0,
  "yong_sin": "목",
  "missing_yong_sin": true
}
```

---

## 제공 Tools (6개)

### 1. `calculate_saju`
사주팔자 전체 계산

```json
// 입력
{
  "birth_date": "2001-08-17",
  "birth_time": "11:00",
  "gender": "male",
  "calendar": "solar",      // "solar" | "lunar"
  "is_leap_month": false
}

// 출력
{
  "year_pillar":  { "stem": "신", "branch": "사", "stem_element": "금", "branch_element": "화", "yin_yang": "음" },
  "month_pillar": { "stem": "병", "branch": "신", "stem_element": "화", "branch_element": "금", "yin_yang": "양" },
  "day_pillar":   { "stem": "임", "branch": "자", "stem_element": "수", "branch_element": "수", "yin_yang": "양" },
  "hour_pillar":  { "stem": "을", "branch": "사", "stem_element": "목", "branch_element": "화", "yin_yang": "음" },
  "wuxing_count": { "목": 1, "화": 3, "토": 0, "금": 2, "수": 2 },
  "dominant_elements": ["화"],
  "weak_elements": ["토"],
  "ten_gods": ["편인", "편재", "비견", "식신"],
  "ten_gods_distribution": { "편재": 1.0, "편인": 0.8, ... },
  "sin_sals": ["cheon_eul_gwi_in", "gwi_mun_gwan_sal"],
  "branch_relations": { "sam_hap": null, "sam_hyeong": [], "yuk_hae": [] },
  "ji_jang_gan": { "year": {...}, "month": {...}, "day": {...}, "hour": {...} },
  "day_master_strength": { "level": "very_strong", "score": 85 },
  "gyeok_guk": { "type": "pyeon_jae", "name": "편재격", "hanja": "偏財格" },
  "yong_sin": { "primary": "목", "secondary": "화", "xi_sin": ["목", "화"], "ji_sin": ["수", "금"] }
}
```

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
{ "birth_date": "2001-08-17", "birth_time": "11:00", "gender": "male", "calendar": "solar", "count": 8 }

// 출력
[
  { "start_age": 3, "end_age": 12, "stem": "정", "branch": "유", "stem_element": "화", "branch_element": "금" },
  { "start_age": 13, "end_age": 22, "stem": "무", "branch": "술", ... },
  ...
]
```

---

### 4. `get_un_flow`
세운(년) / 월운(월) / 시운(시진) 간지 계산

```json
// 입력
{
  "birth_date": "2001-08-17", "birth_time": "11:00",
  "gender": "male", "calendar": "solar",
  "flow_type": "year",   // "year" | "month" | "hour"
  "target": "2025"       // year:"YYYY", month:"YYYY-MM", hour:"HH"
}

// 출력
{
  "stem": "을", "branch": "사",
  "stem_element": "목", "branch_element": "화",
  "ganji_name": "을사년",
  "interaction_with_day_master": "목생화: 일간을 설기하는 기운",
  "interaction_with_yong_sin": "목: 용신과 동일한 오행"
}
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
{
  "total_score": 73,
  "day_pillar_score": 75,
  "element_harmony_score": 68,
  "branch_relation_score": 80,
  "ten_gods_score": 65,
  "complement_elements": ["목"],
  "conflict_branches": ["자-오"]
}
```

---

### 6. `analyze_name`
이름 오행 분석 및 용신 적합도

```json
// 입력
{ "name": "이용재", "birth_date": "2001-08-17", "birth_time": "11:00", "gender": "male" }

// 출력
{
  "name": "이용재",
  "characters": [
    { "char": "이", "consonant": "ㅇ", "element": "토" },
    { "char": "용", "consonant": "ㅇ", "element": "토" },
    { "char": "재", "consonant": "ㅈ", "element": "금" }
  ],
  "element_distribution": { "목": 0, "화": 0, "토": 2, "금": 1, "수": 0 },
  "yong_sin_match_score": 0,
  "yong_sin": "목",
  "missing_yong_sin": true
}
```
