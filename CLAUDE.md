# SajuBon - AI 사주 상담 서비스

## 1. 프로젝트 핵심 컨셉: "Headline-Driven Insights"

AI가 사용자의 사주와 현재 고민을 분석하여 **오직 그 사람만을 위한 결론형 탭 리포트**를 생성합니다.

> "재물운" (X) → "30대 중반, 바위 틈에서 물이 솟구치듯 재물이 터질 팔자" (O)

---

## 2. 전체 시스템 아키텍처

Engine(계산)과 RAG(지식)를 **Python 라이브러리로 직접 임포트**하는 2-Tier 구조입니다.
MCP 프로토콜은 사용하지 않습니다.

```
Frontend (Vue.js 3 / Nuxt.js)
    │  생년월일시 + 성별 + 고민
    ▼
Backend (FastAPI)
    ├─→ engine/        만세력 계산 (4기둥·십성·격국·용신·대운·분석)
    ├─→ rag/           ChromaDB 명리 지식 검색
    ├─→ pipelines/     기능별 파이프라인 조합
    └─→ llm/           Writer Agent (LangChain + PydanticOutputParser)
    ▼
Frontend
    완성된 JSON 1회 반환 → 탭 클릭 = 단순 뷰 전환
```

---

## 3. 4가지 기능 및 파이프라인

### 사주 정밀 분석 `POST /api/saju/calc`
```
Engine.calculate_saju()
  → context_ranking + life_domains
  → RAG 검색 (도메인별 청크)
  → Context Filter (primary 우선 + concern 시맨틱 merge)
  → Writer → 10개 결론형 탭
```

### 궁합 `POST /api/compatibility`
```
Engine.calculate_saju(person1) + Engine.calculate_saju(person2)
  → Synastry Engine (천간합·월지삼합충·용신보완·십성패턴)
  → RAG 검색 (interaction_tags)
  → Writer → 궁합 리포트 (총점 + 항목별 분석)
```

### 오늘의 운세 `POST /api/daily`
```
Engine.calculate_saju() + Engine.get_un_flow(today)
  → Daily Flow (오늘 천간 × 일간 십성, 오늘 지지 × 월지 충합)
  → RAG 검색 (daily_tags)
  → Writer → 오늘 운세 (1탭, 간결)
```

### 한줄 상담 `POST /api/question`
```
Engine.calculate_saju() → behavior_profile + core_keywords
  → 가중 RAG 검색 (question 시맨틱 + saju keywords boost)
  → Writer → 단답형 상담 (1탭, 500자)
```

---

## 4. Engine 12단계 파이프라인

`calculate_saju()` 한 번 호출로 순차 실행:

```
① 4기둥          연·월·일·시주 (진태양시 -30분 보정)
② 십성·12운성    기둥별 태그
③ 신살           역마·도화·화개·귀문관살 등 10종
④ 일간 강약      점수화 (strong/medium/weak)
⑤ 격국           13종
⑥ 용신           억부/조후/통관
⑦ 대운           3일=1년 공식 (10구간)
⑧ 음양 비율      8글자 기준
⑨ 구조패턴       15종 + 동역학(천간합·통근·오행흐름) + 시너지(30규칙)
⑩ 행동프로파일   십성분포 → behavior_vector
⑪ 컨텍스트랭킹   primary 3 + secondary 2
⑫ 생활도메인     career·relationship·wealth·personality
```

---

## 5. RAG 지식 베이스 (ChromaDB)

| 컬렉션 | 문서 수 | 내용 |
|---|---|---|
| ilju | 60 | 60갑자 일주론 (성격·직업·연애) |
| ten_gods | 10 | 십성 해석 (비견~정인) |
| sin_sal | 가변 | 신살 의미 (역마·도화·귀문관살 등) |
| structure_patterns | 가변 | 구조 패턴 해석 |
| dynamics | 가변 | 동역학 해석 |
| wuxing | 가변 | 오행 상생·상극 해석 |

Embedding: Gemini embedding-001

---

## 6. 프로젝트 구조

```
SajuBon/
├── CLAUDE.md
├── README.md
├── frontend/           # Vue.js 3 + Nuxt.js (구현 예정)
└── backend/
    ├── engine/
    │   ├── calc/       # 순수 계산 (15개 모듈)
    │   ├── analysis/   # 후처리 분석 (6개 모듈)
    │   ├── handlers/   # 기능별 핸들러
    │   └── data/       # 정적 명리학 데이터
    ├── rag/            # ChromaDB 검색 + knowledge JSON
    ├── llm/            # Writer LLM (구현 예정)
    ├── pipelines/      # 기능별 파이프라인 (구현 예정)
    ├── routers/        # FastAPI 라우터
    ├── schemas/        # Pydantic 스키마
    ├── db/             # SQLAlchemy 모델·세션
    ├── core/           # pydantic-settings 설정
    └── dependencies/   # FastAPI 의존성
```

---

## 7. 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python 3.10+ (Main), TypeScript (Frontend) |
| Frontend | Vue.js 3, Pinia, Nuxt.js, Tailwind CSS |
| Backend | FastAPI, LangChain (LCEL) |
| AI / LLM | Gemini 2.0 Flash (기본) — Strategy Pattern (OpenAI·Claude 교체 가능) |
| Output Parser | PydanticOutputParser + OutputFixingParser |
| Vector DB | ChromaDB (Gemini embedding-001) |
| Relational DB | PostgreSQL + SQLAlchemy 2.0 (async) |
| Package Manager | uv (Python), pnpm (Node.js) |
| DevOps | Docker, Docker Compose |

---

## 8. 개발 원칙

- Engine과 RAG는 Python 라이브러리로 직접 임포트한다 (MCP 없음).
- 모든 탭 내용은 **한 번에 생성**하여 완성된 JSON을 반환한다 (탭 클릭 = 뷰 전환만).
- 헤드라인은 반드시 **결론형 문장**으로 생성한다 (단순 카테고리명 금지).
- 모든 명리 해석은 RAG 지식 베이스에 근거하여 생성한다.
- LLM은 Strategy Pattern으로 교체 가능하게 설계한다.

---

## 9. 핵심 계산 공식

- **진태양시 보정**: -30분 (동경 127° 보정, 역사적 표준시 자동 적용)
- **연주 기준**: 1984년 = 갑자년, `(year-4)%10` = 천간, `(year-4)%12` = 지지
- **일주 기준일**: 1900-01-01 = 갑술일 (stemIdx=0, branchIdx=10)
- **월주 천간**: 갑·기년→병인월, 을·경년→무인월, 병·신년→경인월, 정·임년→임인월, 무·계년→갑인월
- **시주 천간**: `(일간index*2 + 시지index) % 10`
- **대운 공식**: 3일=1년, 1일=4개월, 1시진(2h)=10일, 최대 10세
- **24절기**: ephem 라이브러리 실시간 천문 계산
- **음력 변환**: korean-lunar-calendar 패키지
