# Backend — FastAPI AI 파이프라인 서버

4가지 기능별 AI 파이프라인을 오케스트레이션합니다.
Engine(사주 계산)과 RAG(지식 검색)를 **Python 라이브러리로 직접 임포트** — 네트워크 오버헤드 없음.

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
├── llm/                            # Writer LLM (구현 예정)
│   ├── providers.py                # LLM Strategy Pattern (Gemini/OpenAI/Claude)
│   ├── prompt_manager.py           # 기능별 마스터 프롬프트 (4종)
│   ├── output_schemas.py           # PydanticOutputParser 스키마
│   └── agent.py                    # Writer Agent (LangChain LCEL)
│
├── pipelines/                      # 기능별 파이프라인 (구현 예정)
│   ├── saju_analysis.py            # Engine → RAG → Context Filter → Writer
│   ├── compatibility.py            # Engine×2 → Synastry → RAG → Writer
│   ├── daily_fortune.py            # Engine + 오늘간지 → Daily Tags → RAG → Writer
│   └── quick_question.py           # Engine → 가중 RAG → Writer
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

## 구현 완료 엔드포인트

### `POST /api/saju/calc` — 사주팔자 계산

생년월일시와 성별로 사주 전체를 계산합니다.

**요청**
```json
{
  "birth_date": "1990-03-15",
  "birth_time": "14:30",
  "gender": "male",
  "calendar": "solar",
  "is_leap_month": false
}
```

**응답 구조 (주요 필드)**
```
meta                  계산 메타 (시각 보정 분수, 기후 정보)
day_master_strength   일간 강약 (level: strong/medium/weak, score 0~100)
yong_sin              용신·희신·기신 오행
gyeok_guk             격국 (칠살격·정관격·식신격 등)
year/month/day/hour_pillar  4기둥 (십성·12운성 포함)
wuxing_count          오행별 비율% (0 포함)
ten_gods_distribution 십성별 비율% (0 제외)
sin_sals              신살 목록 (priority 포함)
branch_relations      지지 관계 (충·합·형·해·파)
ji_jang_gan           지장간
dae_un_list           대운 10구간
current_dae_un        현재 대운 (십성 포함)
dynamics              기둥 간 동역학
synergy               구조패턴 × 동역학 시너지
behavior_profile      행동 벡터 태그 목록
context_ranking       RAG 우선순위 (primary·secondary)
life_domains          도메인별 태그 (career·relationship·wealth·personality)
```

> Swagger UI: `http://localhost:8000/docs`

---

## 4가지 기능 파이프라인 (구현 예정)

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

## 실행

```bash
cd backend
cp .env.example .env
# GEMINI_API_KEY=..., DATABASE_URL=postgresql+asyncpg://...

uv sync --group dev
uv run uvicorn main:app --reload --port 8000
# Swagger: http://localhost:8000/docs
```

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
