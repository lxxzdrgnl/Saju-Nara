# Backend — FastAPI AI 파이프라인 서버

## 프로젝트 개요

기존 운세 서비스는 미리 준비된 텍스트를 조건별로 출력합니다. SajuBon은 사용자의 **사주팔자 계산 결과**와 **현재 고민**을 AI가 교차 분석해 그 사람에게만 해당하는 결론형 탭 리포트를 생성합니다.

> "재물운" (X) → "30대 중반, 바위 틈에서 물이 솟구치듯 재물이 터질 팔자" (O)

**주요 기능**

| # | 기능 | 설명 |
|---|---|---|
| 1 | 사주 정밀 분석 | 생년월일시 + 고민 → 12단계 계산 → RAG 지식 검색 → AI 10탭 리포트 생성 |
| 2 | 궁합 | 두 사람의 사주 + Synastry 분석 → AI 궁합 리포트 |
| 3 | 오늘의 운세 | 사주 + 오늘 간지 × 일간 십성 관계 → AI 일운 리포트 |
| 4 | 한줄 상담 | 사주 + 질문 → 가중 RAG 검색 → AI 단답 상담 |

Engine(사주 계산)과 RAG(지식 검색)를 **Python 라이브러리로 직접 임포트** — 네트워크 오버헤드 없음.

---


## 실행

```bash
cd backend
cp .env.example .env
# .env에 GEMINI_API_KEY, DATABASE_URL 입력

# 의존성 설치
uv sync --group dev

# DB 마이그레이션 (PostgreSQL 사용 시)
uv run alembic upgrade head

# ChromaDB 초기 인덱싱 (최초 1회 또는 knowledge JSON 변경 시)
uv run python -c "from rag.ingest import ingest_all; ingest_all()"

# 서버 실행
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 배포 주소

| 환경 | URL |
|---|---|
| 로컬 Base URL | `http://localhost:8000` |
| 로컬 Swagger UI | `http://localhost:8000/docs` |
| 로컬 ReDoc | `http://localhost:8000/redoc` |
| 로컬 Health Check | `http://localhost:8000/health` |

---

## 기술 스택

| 항목 | 기술 |
|---|---|
| Framework | FastAPI |
| Pipeline | LangChain (LCEL) |
| LLM | Gemini 2.0 Flash (기본) — Strategy Pattern |
| Output Parser | PydanticOutputParser + OutputFixingParser |
| Vector DB | ChromaDB (Gemini embedding-001) |
| Relational DB | PostgreSQL + SQLAlchemy 2.0 (async) |
| Migration | Alembic |
| Package Manager | uv |

---

## 환경변수

`.env.example`을 복사해 `.env`를 작성합니다.

| 변수 | 필수 | 기본값 | 설명 |
|---|---|---|---|
| `LLM_PROVIDER` | — | `gemini` | LLM 선택 (`gemini` \| `openai` \| `claude`) |
| `GEMINI_API_KEY` | LLM_PROVIDER=gemini 시 필수 | — | Google AI Studio에서 발급 |
| `OPENAI_API_KEY` | LLM_PROVIDER=openai 시 필수 | — | OpenAI 플랫폼에서 발급 |
| `ANTHROPIC_API_KEY` | LLM_PROVIDER=claude 시 필수 | — | Anthropic Console에서 발급 |
| `EMBEDDING_PROVIDER` | — | `gemini` | 임베딩 모델 제공사 |
| `EMBEDDING_MODEL` | — | `gemini-embedding-001` | 임베딩 모델명 |
| `CHROMA_PATH` | — | `../mcp-servers/saju-rag/chroma_db` | ChromaDB 경로 |
| `DATABASE_URL` | PostgreSQL 사용 시 필수 | — | `postgresql+asyncpg://user:pw@host:5432/db` |
| `PORT` | — | `8000` | 서버 포트 |

---

## 엔드포인트 요약

| 메서드 | URL | 기능 | 인증 |
|---|---|---|---|
| POST | `/api/saju/calc` | 사주팔자 12단계 계산 | 불필요 |
| POST | `/api/compatibility` | 궁합 분석 (구현 예정) | 불필요 |
| POST | `/api/daily` | 오늘의 운세 (구현 예정) | 불필요 |
| POST | `/api/question` | 한줄 상담 (구현 예정) | 불필요 |
| GET | `/r/{token}` | 리포트 공유 링크 (구현 예정) | 불필요 |
| GET | `/health` | 서버 상태 확인 | 불필요 |
| GET | `/docs` | Swagger UI | 불필요 |
| GET | `/redoc` | ReDoc | 불필요 |

---

## 모듈 구조

```
backend/
├── main.py                         # FastAPI 앱 진입점
├── pyproject.toml
├── .env.example
│
├── engine/                         # 만세력 계산 엔진
│   ├── calc/                       # 순수 계산 모듈 (15개)
│   │   ├── saju.py                 # 4기둥 계산 (연·월·일·시주)
│   │   ├── ten_gods.py             # 십성·12운성 계산
│   │   ├── sin_sal.py              # 신살 판단 (역마·도화·화개 등 10종)
│   │   ├── day_master_strength.py  # 일간 강약 점수화
│   │   ├── gyeok_guk.py            # 격국 판단 (13종)
│   │   ├── yong_sin.py             # 용신 선정 (억부/조후/통관)
│   │   ├── dae_un.py               # 대운 계산 (3일=1년 공식)
│   │   ├── se_un.py                # 세운 계산
│   │   ├── twelve_wun.py           # 12운성 계산
│   │   ├── solar_terms.py          # ephem 24절기 실시간 계산
│   │   ├── calendar_converter.py   # 음양력 변환 (korean-lunar-calendar)
│   │   ├── compatibility.py        # 궁합 점수 계산
│   │   ├── daily_flow.py           # 오늘 간지 × 사주 십성 관계
│   │   ├── synastry.py             # 두 사주 상호작용 태그 (궁합용)
│   │   ├── validation.py           # 입력 검증
│   │   └── models.py               # BirthInput / PersonInput Pydantic 스키마
│   │
│   ├── analysis/                   # 후처리 분석 파이프라인 (6개)
│   │   ├── structure_patterns.py   # 구조 패턴 감지 (식상생재·관인상생 등 15종)
│   │   ├── dynamics.py             # 기둥 간 동역학 (천간합·통근·오행흐름)
│   │   ├── synergy.py              # 구조패턴 × 동역학 교차 시너지 (30규칙)
│   │   ├── behavior_synthesizer.py # 십성 분포 → 행동 벡터 합성
│   │   ├── context_ranker.py       # RAG 우선순위화 (primary 3 + secondary 2)
│   │   └── life_domain_mapper.py   # career·relationship·wealth·personality 분류
│   │
│   ├── handlers/                   # 기능별 계산 핸들러 (calc + analysis 조합)
│   │   ├── calculate_saju.py       # 12단계 파이프라인 전체 실행
│   │   ├── check_compatibility.py  # 궁합 점수 핸들러
│   │   ├── get_dae_un.py           # 대운 목록 핸들러
│   │   ├── get_un_flow.py          # 세운·월운·일운 흐름 핸들러
│   │   └── convert_calendar.py     # 음양력 변환 핸들러
│   │
│   └── data/                       # 정적 명리학 데이터
│       ├── heavenly_stems.py       # 천간 10개 (오행·음양·한자)
│       ├── earthly_branches.py     # 지지 12개 (지장간·충합형해)
│       ├── wuxing.py               # 오행 상생·상극 관계
│       └── timezone_history.py     # 역사적 한국 표준시 변환 테이블
│
├── rag/                            # ChromaDB 기반 명리학 지식 검색
│   ├── db.py                       # ChromaDB 연결·검색 함수
│   ├── ingest.py                   # 지식 JSON → ChromaDB 인덱싱
│   ├── search.py                   # 컨텍스트 기반 검색 핸들러
│   ├── providers.py                # Embedding Strategy Pattern (Gemini/OpenAI)
│   └── knowledge/                  # 명리학 지식 JSON (105개 문서)
│       ├── ilju.json               # 60갑자 일주론 (60개)
│       ├── ten_gods.json           # 십성 해석 (10개)
│       ├── sin_sal.json            # 신살 의미
│       ├── structure_patterns.json # 구조 패턴 해석
│       ├── dynamics.json           # 동역학 해석
│       └── wuxing.json             # 오행 상생·상극 해석
│
├── llm/                            # Writer LLM + 파이프라인 (구현 예정)
│   ├── providers.py                # LLM Strategy Pattern (Gemini/OpenAI/Claude)
│   ├── prompt_manager.py           # 기능별 마스터 프롬프트 (4종)
│   ├── output_schemas.py           # PydanticOutputParser 스키마
│   ├── agent.py                    # Writer Agent (LangChain LCEL)
│   └── pipelines/                  # 기능별 파이프라인
│       ├── saju_analysis.py        # Engine → RAG → Context Filter → Writer
│       ├── compatibility.py        # Engine×2 → Synastry → RAG → Writer
│       ├── daily_fortune.py        # Engine + 오늘간지 → Daily Tags → RAG → Writer
│       └── quick_question.py       # Engine → 가중 RAG → Writer
│
├── routers/                        # FastAPI 라우터
│   ├── saju.py                     # POST /api/saju/calc  ← 구현 완료
│   ├── compatibility.py            # POST /api/compatibility (구현 예정)
│   ├── daily.py                    # POST /api/daily (구현 예정)
│   └── question.py                 # POST /api/question (구현 예정)
│
├── schemas/                        # Pydantic 요청/응답 스키마
│   ├── saju.py                     # SajuCalcRequest / SajuCalcResponse
│   └── report.py                   # BirthRequest / ReportResponse 공통
│
├── db/                             # 데이터베이스
│   ├── models.py                   # SQLAlchemy 2.0+ 모델 (Report·User)
│   └── session.py                  # async 세션 팩토리
│
├── core/
│   └── config.py                   # pydantic-settings 앱 설정
│
└── dependencies/
    ├── auth.py                     # 인증 의존성 (현재 stub — JWT 확장 예정)
    └── db.py                       # DB 세션 의존성
```

---

## 에러 처리

### 에러 응답 공통 포맷

모든 API 오류는 아래 구조로 반환됩니다.

```json
{
  "timestamp": "2025-08-17T11:00:00Z",
  "path": "/api/saju/calc",
  "status": 422,
  "code": "VALIDATION_FAILED",
  "message": "입력값 검증에 실패했습니다.",
  "details": {
    "birth_date": "지원 연도 범위: 1900~2100, 입력값: 1800-01-01",
    "gender": "허용값: male | female, 입력값: 'M'"
  }
}
```

### 에러 코드 정의

| HTTP | 코드 | 설명 |
|---|---|---|
| 400 | `BAD_REQUEST` | 요청 형식 오류 |
| 400 | `VALIDATION_FAILED` | 필드 유효성 검사 실패 (details에 필드별 오류 포함) |
| 400 | `INVALID_DATE_FORMAT` | 날짜 형식 오류 (YYYY-MM-DD 아님) |
| 400 | `INVALID_BIRTH_YEAR` | 지원 범위 외 연도 (허용: 1900~2100) |
| 400 | `INVALID_QUERY_PARAM` | 쿼리 파라미터 값 오류 |
| 401 | `UNAUTHORIZED` | 인증 토큰 없음·잘못된 토큰 |
| 401 | `TOKEN_EXPIRED` | 토큰 만료 |
| 403 | `FORBIDDEN` | 접근 권한 없음 |
| 404 | `RESOURCE_NOT_FOUND` | 리소스 없음 |
| 404 | `REPORT_NOT_FOUND` | share_token 리포트 없음 |
| 404 | `USER_NOT_FOUND` | 사용자 ID 없음 |
| 409 | `DUPLICATE_RESOURCE` | 중복 데이터 (이메일 등) |
| 409 | `STATE_CONFLICT` | 리소스 상태 충돌 |
| 422 | `UNPROCESSABLE_ENTITY` | 형식은 맞으나 논리적 오류 |
| 422 | `CALC_FAILED` | 사주 계산 처리 실패 |
| 429 | `TOO_MANY_REQUESTS` | 요청 한도 초과 |
| 500 | `INTERNAL_SERVER_ERROR` | 서버 내부 오류 |
| 500 | `DATABASE_ERROR` | DB 연동 오류 |
| 500 | `UNKNOWN_ERROR` | 알 수 없는 오류 (최종 fallback) |

### 예외 처리 흐름

```python
# core/exceptions.py — 커스텀 예외 클래스 (ErrorCode와 1:1 매핑)
raise ValidationException("...", details={"birth_date": "..."})
raise InvalidDateFormatException("1990/03/15")
raise CalcFailedException("에러 원인")

# main.py — 전역 예외 핸들러
@app.exception_handler(AppException)        # 커스텀 예외 → ErrorResponse 직렬화
@app.exception_handler(RequestValidationError)  # Pydantic 검증 실패 → VALIDATION_FAILED
@app.exception_handler(Exception)           # 미처리 예외 → 500 + 서버 스택트레이스 로그
```

---

## 로깅

### Access Log (요청/응답 요약)

`middleware/logging.py` — 모든 요청을 자동으로 기록합니다.

```
2025-08-17T11:00:01 [INFO] sajubon.access — POST /api/saju/calc  status=200  time=312ms  ip=127.0.0.1
2025-08-17T11:00:02 [INFO] sajubon.access — GET /health  status=200  time=1ms  ip=127.0.0.1
2025-08-17T11:00:03 [INFO] sajubon.access — POST /api/saju/calc  status=422  time=5ms  ip=127.0.0.1
```

### Error Log (스택트레이스)

처리되지 않은 예외 발생 시 `sajubon` 로거로 스택트레이스를 기록합니다.
응답 body에는 민감정보 없이 `INTERNAL_SERVER_ERROR`만 반환됩니다.

```
2025-08-17T11:00:05 [ERROR] sajubon — Unhandled exception: POST /api/saju/calc
Traceback (most recent call last):
  File ".../engine/handlers/calculate_saju.py", line 50, in handle_calculate_saju
    ...
```

### 로그 설정

```python
# main.py
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
```
---

## Engine — 사주팔자 계산

### 핵심 계산 공식

| 항목 | 공식 |
|---|---|
| 진태양시 보정 | 동경 127° 기준, 역사적 표준시 자동 적용 (통상 -30~-32분) |
| 연주 기준 | 1984년 = 甲子년, `(year-4)%10` = 천간, `(year-4)%12` = 지지 |
| 일주 기준일 | 1900-01-01 = 甲戌일 (stemIdx=0, branchIdx=10) |
| 월주 천간 | 갑·기년→丙寅, 을·경년→戊寅, 병·신년→庚寅, 정·임년→壬寅, 무·계년→甲寅 |
| 시주 천간 | `(일간index × 2 + 시지index) % 10` |
| 대운 공식 | 3일=1년, 1일=4개월, 1시진(2h)=10일, 최대 10세 |
| 24절기 | ephem 라이브러리 실시간 천문 계산 |
| 음력 변환 | korean-lunar-calendar 패키지 |

### 시주(時柱) — 12시진 대응표

사용자는 **KST(한국 표준시)** 로 입력하고, 엔진이 내부적으로 진태양시로 변환 후 시진을 결정합니다.
아래 표는 **KST 입력 기준** 범위입니다 (현대 기준 -30분 보정 적용).

| 시진 | KST 입력 범위 | 진태양시 범위 | 지지 |
|---|---|---|---|
| 자시(子時) | 23:30~01:29 | 23:00~00:59 | 자(子) |
| 축시(丑時) | 01:30~03:29 | 01:00~02:59 | 축(丑) |
| 인시(寅時) | 03:30~05:29 | 03:00~04:59 | 인(寅) |
| 묘시(卯時) | 05:30~07:29 | 05:00~06:59 | 묘(卯) |
| 진시(辰時) | 07:30~09:29 | 07:00~08:59 | 진(辰) |
| **사시(巳時)** | **09:30~11:29** | 09:00~10:59 | 사(巳) |
| 오시(午時) | 11:30~13:29 | 11:00~12:59 | 오(午) |
| 미시(未時) | 13:30~15:29 | 13:00~14:59 | 미(未) |
| 신시(申時) | 15:30~17:29 | 15:00~16:59 | 신(申) |
| 유시(酉時) | 17:30~19:29 | 17:00~18:59 | 유(酉) |
| 술시(戌時) | 19:30~21:29 | 19:00~20:59 | 술(戌) |
| 해시(亥時) | 21:30~23:29 | 21:00~22:59 | 해(亥) |

> **이용재 예시**: KST 11:00 → 내부 보정 -32분 → 진태양시 10:28 → **사시(巳時)** ✓
> 11:30 KST 미만이므로 사시. 만약 11:30 이후에 태어났다면 오시가 됩니다.
>
> 정확한 보정값은 시대(1961년 이후 -32분)에 따라 자동 적용됩니다.

---

## 구현 완료 엔드포인트

### `POST /api/saju/calc` — 사주팔자 계산

생년월일시와 성별로 사주 전체를 계산합니다.

**요청**
```json
{
  "birth_date": "2001-08-17",
  "birth_time": "11:00",
  "gender": "male",
  "calendar": "solar",
  "is_leap_month": false
}
```

**응답 구조 (주요 필드)**
```
meta                  계산 메타 (시각 보정 분수, 기후 정보)
day_master_strength   일간 강약 (level: strong/medium/very_strong/weak/very_weak, score 0~100)
yong_sin              용신·희신·기신 오행
gyeok_guk             격국 (편재격·칠살격·정관격·식신격 등)
year/month/day/hour_pillar  4기둥 (십성·12운성 포함)
wuxing_count          오행별 비율% (0 포함 — 결핍 오행도 의미 있음)
ten_gods_distribution 십성별 비율% (0 제외, 합산 ~100)
ten_gods_void_info    결핍 카테고리 + 지장간 잠재력 대조
structure_patterns    구조 패턴 목록
sin_sals              신살 목록 (priority: high/medium/low)
branch_relations      지지 관계 (충·합·형·해·파)
ji_jang_gan           지장간
dae_un_list           대운 10구간
current_dae_un        현재 대운 (십성 포함)
dynamics              기둥 간 동역학 (stem_hap·rooting_map·active_relations·energy_flow)
synergy               구조패턴 × 동역학 시너지 리스트
behavior_profile      행동 벡터 태그 목록
context_ranking       RAG 우선순위 (primary 3 + secondary 2)
life_domains          career·relationship·wealth·personality 태그 분류
```

> Swagger UI: `http://localhost:8000/docs`

---

## 4가지 기능 파이프라인 (`llm/pipelines/`, 구현 예정)

### 1. 사주 정밀 분석

```
calculate_saju() → context_ranking + life_domains
    → RAG 검색 (도메인별 청크)
    → Context Filter (primary 우선 재정렬 + concern 시맨틱 merge)
    → Writer → 10개 결론형 탭
```

### 2. 궁합

```
calculate_saju(person1) + calculate_saju(person2)
    → Synastry Engine (천간합·월지삼합충·용신보완·십성패턴)
    → RAG 검색 (interaction_tags 기준)
    → Writer → 궁합 리포트 (총점 + 항목별 분석)
```

### 3. 오늘의 운세

```
calculate_saju() + get_un_flow(today)
    → Daily Flow (오늘 천간 × 일간 십성, 오늘 지지 × 월지 충합)
    → RAG 검색 (daily_tags 기준)
    → Writer → 오늘 운세 (1탭, 간결)
```

### 4. 한줄 상담

```
calculate_saju() → behavior_profile + core_keywords
    → 가중 RAG 검색 (question 시맨틱 + saju keywords boost)
    → Writer → 단답형 상담 (1탭, 500자)
```

---

## 인증 플로우

현재 모든 API는 인증 없이 공개 접근 가능합니다 (MVP 단계).
향후 JWT 기반 인증이 추가될 예정이며, `dependencies/auth.py`에 stub이 준비되어 있습니다.

```
[클라이언트]
    │  Authorization: Bearer <JWT>
    ▼
[FastAPI 의존성 — dependencies/auth.py]
    │  토큰 검증 실패 → 401 UNAUTHORIZED / 401 TOKEN_EXPIRED
    │  권한 부족     → 403 FORBIDDEN
    ▼
[라우터 핸들러]
```

### 역할/권한표

| 역할 | 접근 가능 API | 설명 |
|---|---|---|
| 비로그인 (anonymous) | 모든 계산 API, `/health`, `/docs` | 리포트 저장 없이 계산만 가능 |
| ROLE_USER | 비로그인 + 리포트 저장·조회·공유 | JWT 발급 후 이용 |
| ROLE_ADMIN | 전체 + 사용자 관리·지식베이스 재인덱싱 | 내부 운영 전용 |

> 현재 구현 단계에서는 모든 엔드포인트가 anonymous 수준으로 동작합니다.

---

## Writer LLM Strategy Pattern

```python
# llm/providers.py
# .env: LLM_PROVIDER=gemini (기본) | openai | claude

# 지원 모델
#   gemini → gemini-2.0-flash
#   openai → gpt-4o
#   claude → claude-sonnet-4-6
```

## Output Parser

```python
# llm/output_schemas.py
class TabContent(BaseModel):
    headline: str   # 결론형 헤드라인 (단순 카테고리명 금지)
    body: str       # 상세 내용 (마크다운)

class ReportOutput(BaseModel):
    tabs: list[TabContent]

# llm/agent.py — LLM 오류 시 OutputFixingParser 자동 재시도
parser = PydanticOutputParser(pydantic_object=ReportOutput)
fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=get_llm())
chain = prompt | llm | fixing_parser
```

---

## DB 모델

```python
class Report(Base):
    feature:     str       # saju / compatibility / daily / question
    share_token: UUID      # GET /r/{token} 공유 링크
    user_id:     int|None  # nullable — 비로그인 익명 허용
    input_data:  JSONB     # 원본 요청
    calc_result: JSONB     # Engine 출력
    rag_chunks:  JSONB     # RAG 검색 결과
    output:      JSONB     # Writer 최종 출력

class User(Base):
    plan: str  # free / pro / premium
```

---

---

## RAG — 명리학 지식 검색

### 지식 베이스 구조

ChromaDB 6개 컬렉션, 총 105개 문서. Gemini embedding-001로 인덱싱.

| 컬렉션 | 문서 수 | 내용 |
|---|---|---|
| `ilju` | 60 | 60갑자 일주론 — 아키타입·직업·연애·취약점·일주 간 궁합 |
| `ten_gods` | 10 | 십성(十星) — 비견~정인 각 특성·발현 방식 |
| `sin_sal` | 가변 | 신살(神殺) — 역마·도화·귀문관살·원진·천을귀인 등 의미·발동 조건 |
| `structure_patterns` | 가변 | 구조 패턴 — 인다신강·식상생재·관인상생 등 15종 해석 |
| `dynamics` | 가변 | 동역학 — 천간합·충·삼합 등 기둥 간 상호작용 해석 |
| `wuxing` | 가변 | 오행 — 상생·상극·조후 관계별 해석 |

### 검색 API

```python
# rag/search.py

# 1. 사주 전체 컨텍스트 기반 조합 검색 (파이프라인 메인 입력)
handle_search_by_context(
    context_ranking,  # calc의 context_ranking 필드
    life_domains,     # calc의 life_domains 필드
    day_pillar,       # 일주 간지 — ilju 직접 조회
    concern,          # 사용자 고민 원문 — 시맨틱 검색 추가
    n_per_domain=2,   # 도메인별 결과 수
) -> {
    "career":       [RAG chunk, ...],
    "relationship": [RAG chunk, ...],
    "wealth":       [RAG chunk, ...],
    "personality":  [RAG chunk, ...],
    "context":      [RAG chunk, ...],   # primary_context 직접 조회
    "ilju":         {일주 전체 지식},
    "concern":      [RAG chunk, ...],   # concern 있을 때만
}

# 2. 단건 조회
handle_get_ilju_profile("임자")         # 일주론 전체 JSON
handle_get_ten_god_profile("편재")      # 십성 프로파일
handle_get_structure_pattern("in_da_sin_gang")  # 구조 패턴
handle_get_sin_sal_profile("양인살")    # 신살 프로파일

# 3. 자유 시맨틱 검색
handle_search_knowledge(query, collection, n_results=5)
```

### 일주론 데이터 구조 (ilju 컬렉션)

```json
{
  "id":         "ij_imja",
  "ilju":       "임자",
  "hanja":      "壬子",
  "archetype":  "deep_analytical_type",
  "common_expression": ["철학", "연구", "심연", "독립", "관찰", "침묵", "통찰"],
  "element_concentration": "壬水(양수) + 子水(비견) — 수기 극집중",
  "psychological_traits": ["deep_inner_world", "cold_exterior_warm_interior", "analytical_depth"],
  "career_affinity": {
    "domains":  ["analysis", "philosophy", "research", "security", "writing", "counseling"],
    "examples": ["연구자", "데이터 분석가", "전략 컨설턴트", "작가", "심리상담사", "정보보안 전문가"]
  },
  "relationship_style": ["passive_initiator", "deep_unwavering_when_committed"],
  "strength":   ["탁월한_분석력", "독립심", "흔들리지_않는_중심"],
  "vulnerability": {
    "trait":     "감정 표현 부족, 고독, 과도한 사색으로 행동 지연",
    "safeguard": "소규모 글쓰기·스터디처럼 안전한 표현의 출구 환경"
  },
  "compatibility": {
    "harmonious": [{"ilju": "계축", "reason": "子丑 육합 — 음양의 결합", "tag": "yuk_hap"}],
    "conflict":   [{"ilju": "병오", "reason": "子午 충 + 壬丙 수화 상극", "tag": "chung"}]
  },
  "consulting_points": {
    "empathy_trigger": "아무도 당신의 깊이를 제대로 알아주지 않는다는 외로움을 느끼시나요?",
    "solution_speech": "당신의 수기(水氣)는 흐르지 않으면 고여서 마음의 병이 됩니다 — 글쓰기, 강의, 창작물이 물길을 내는 통로입니다.",
    "tab_headline":    "가장 차가운 물이 가장 깊은 곳에 있습니다"
  },
  "tags": ["심오함", "지혜", "독립", "철학", "냉철", "고독철학자", "내면온기역설"]
}
```

> 이용재(2001-08-17) 일주 **임자(壬子)** 기준 실제 조회 결과입니다.

### 인덱싱

```bash
# 최초 실행 또는 knowledge JSON 변경 시
uv run python -c "from rag.ingest import ingest_all; ingest_all()"

# 특정 컬렉션만 재인덱싱
uv run python -c "from rag.ingest import ingest; ingest('ilju')"
```

---

## 예시 계산 — 이용재 (2001-08-17 양력, 오전 11시생)

> 출생 시각 11:00 → 진태양시 보정 -32분 → **10:28** → 사시(巳時, 09:00~10:59) 적용

**입력**
```json
{
  "birth_date": "2001-08-17",
  "birth_time": "11:00",
  "gender": "male",
  "calendar": "solar"
}
```

**메타**
```
음력:         2001년 6월 28일 (입추 이후)
시각 보정:    11:00 - 32분 = 10:28 → 사시(巳時) 적용 (오시 아님!)
기후:         가을 / 서늘 / 건조 (월지 申金 → 壬水 생)
```

**사주팔자**

| 기둥 | 천간 | 지지 | 오행 | 십성 | 12운성 |
|---|---|---|---|---|---|
| 연주(年柱) | 신(辛) | 사(巳) | 금·화 | 정인·편재 | 사 |
| 월주(月柱) | 병(丙) | 신(申) | 화·금 | 편재·편인 | 병 |
| 일주(日柱) | **임(壬)** | **자(子)** | **수·수** | **비견·겁재** | **제왕** |
| 시주(時柱) | **을(乙)** | **사(巳)** | **목·화** | **상관·편재** | **목욕** |

> ※ 11:00 입력 시 보정 후 사시(巳時)로 결정 → 시주 **을사(乙巳)**. 12:00 입력 시 오시(午時) 적용으로 시주 달라짐.

**오행 분포**

| 오행 | 비율 | 해석 |
|---|---|---|
| 목(木) | 12.5% | 용신 — 부족하나 존재 |
| 화(火) | 37.5% | 과다 |
| 토(土) | 0.0% | **결핍** |
| 금(金) | 25.0% | 보통 |
| 수(水) | 25.0% | 보통 |

음양 비율: 양 62.5% / 음 37.5%

**지장간**

| 기둥 | 지장간 |
|---|---|
| 연지 巳 | 병(丙)·무(戊)·경(庚) |
| 월지 申 | 경(庚)·임(壬)·무(戊) |
| 일지 子 | 계(癸) |
| 시지 巳 | 병(丙)·무(戊)·경(庚) |

**지지 관계**

| 관계 | 내용 |
|---|---|
| 육합(六合) | 사(巳) + 신(申) → 수(水) 화합 (방해 없음, 유효) |

> 자오충 없음 — 시주가 午→巳로 바뀌어 충 관계 해소

**일간 강약**

```
level:   very_strong (score: 100)
월령:    得令 — 申月에 壬水가 득기
분석:    월령을 득하여 강함. 비겁 극소. 인성 적절
```

**격국 · 용신**

| 항목 | 결과 |
|---|---|
| 격국 | **편재격(偏財格)** — 사교적·사업수완 뛰어난 활동형 |
| 용신 | **목(木)** — 수 과강, 목으로 설기 |
| 희신 | 목(木)·화(火) |
| 기신 | 수(水)·금(金) |
| 논리 | 억부 — overpowered_day_master_drain |

**십성 분포**

| 십성 | 비율 |
|---|---|
| 편재(偏財) | 33.3% |
| 편인(偏印) | 25.0% |
| 상관(傷官) | 16.7% |
| 정인(正印) | 16.7% |
| 겁재(劫財) | 8.3% |

결핍 카테고리: 관성(官星) — 지장간에 무(戊)·기(己) 잠재

**구조 패턴**

| 패턴 | 의미 |
|---|---|
| 식상생재(食傷生財) | 상관이 편재를 생함 — 아이디어가 곧 수입 (콘텐츠·창업) |
| 상관패인(傷官佩印) | 상관 + 인성 공존 — 날카로운 비판 지성, 지식 기반 반골 |
| 인다신강(印多身强) | 인성 과다 신강 — 이론 풍부, 실천력 보완 필요 |

**신살**

| 신살 | 종류 | 위치 | 우선순위 | 설명 |
|---|---|---|---|---|
| 천을귀인(天乙貴人) | lucky | 연지 巳 | medium | 위기 시 귀인의 도움 |
| **귀문관살(鬼門關殺)** | unlucky | 연·월 (巳申) | **high** | 예민한 직관·신경과민 주의 |
| **양인살(羊刃殺)** | unlucky | 일지 子 | **high** | 강한 추진력·다혈질 |

> 12:00 입력 시 발동하던 도화살·역마살·원진살은 시주 변경으로 소멸

**대운**

대운 시작 나이: **4세** (순행)

| 나이 | 천간·지지 | 오행 |
|---|---|---|
| 4~13세 | 을미(乙未) | 목·토 |
| 14~23세 | 갑오(甲午) | 목·화 |
| **24~33세** | **계사(癸巳)** | **수·화** |
| 34~43세 | 임진(壬辰) | 수·토 |

현재 대운 (24~33세): 癸巳 — 겁재·편재 (수 기운 가중, 巳火로 재성 자극)

**행동 프로파일 · 생활 도메인**

```
behavior_profile: [opportunistic_action, resource_mobilization, unconventional_intuition,
                   independent_learning, risk_taking, critical_analysis]

career:       [opportunistic_action, resource_mobilization, content_creator]
wealth:       [opportunistic_action, resource_mobilization, creative_income]
relationship: []
personality:  [unconventional_intuition, independent_learning, risk_taking]
```

**RAG 컨텍스트 우선순위**

```
primary:   식상생재(85.0) · 양인살(85.0) · 귀문관살(83.0)
secondary: 상관패인(60.0) · 인다신강(60.0)
```
