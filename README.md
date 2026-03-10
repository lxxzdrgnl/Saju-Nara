# SajuBon

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3.0-4FC08D?style=flat-square&logo=vue.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=flat-square&logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-Writer_LLM-4285F4?style=flat-square&logo=google&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-FF6B35?style=flat-square)

**AI가 당신의 사주(四柱)와 오늘의 고민을 함께 읽어드립니다.**

> "재물운" (X)
> "30대 중반, 바위 틈에서 물이 솟구치듯 재물이 터질 팔자" (O)
---

## 사주팔자(四柱八字)란?

태어난 **연·월·일·시** 네 기둥(四柱), 여덟 글자(八字)로 이루어진 동양 명리학의 핵심입니다.

| 기둥 | 의미 |
|---|---|
| 연주(年柱) | 조상·초년운 |
| 월주(月柱) | 부모·청장년운 |
| 일주(日柱) | 본인·배우자·중년운 |
| 시주(時柱) | 자녀·노년운 |
---

## 프로젝트 개요

기존 운세 서비스는 미리 준비된 텍스트를 조건별로 출력합니다. SajuBon은 사용자의 **사주팔자 계산 결과**와 **현재 고민**을 AI가 교차 분석해 그 사람에게만 해당하는 결론형 탭 리포트를 생성합니다.

**주요 기능**

| # | 기능 | 엔드포인트 | 파이프라인 |
|---|---|---|---|
| 1 | 사주 정밀 분석 | `POST /api/saju/calc` | Engine → RAG → Context Filter → Writer (10탭) |
| 2 | 궁합 | `POST /api/compatibility` | Engine×2 → Synastry → RAG → Writer |
| 3 | 오늘의 운세 | `POST /api/daily` | Engine + 오늘간지 → Daily Tags → RAG → Writer |
| 4 | 한줄 상담 | `POST /api/question` | Engine → 가중 RAG 검색 → Writer |

---

## 핵심 컨셉: Headline-Driven Insights

사주 계산 결과와 사용자의 실제 고민을 AI가 교차 분석해 **오직 당신만을 위한 결론형 탭 리포트**를 생성합니다.

```
입력: "2001-08-17 11:00 남성 + 회사 상사와 갈등이 심해 이직을 고민 중입니다"

출력:
  탭 1. 임자일주, 가장 차가운 물이 가장 깊은 곳에 있습니다 — 그 고집이 상사와 정면충돌
  탭 2. 식상생재격 + 현 대운 계사(癸巳) — 창의적 실행이 곧 수입이 되는 시기
  탭 3. 용신 목(木)·화(火)가 강한 콘텐츠·IT 계열에서 귀문관살의 직관이 빛을 발함
  탭 4. 귀문관살 + 상관패인 — 날카로운 비판 지성이 무기이자 조직 내 갈등의 씨앗
  ...
```

---

## 레이어별 상세 문서

| 레이어 | 경로 | 문서 |
|---|---|---|
| Frontend | [frontend/](./frontend) | [frontend/README.md](./frontend/README.md) |
| Backend | [backend/](./backend) | [backend/README.md](./backend/README.md) |

---

## 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python 3.10+, TypeScript |
| Frontend | Vue.js 3, Pinia, Nuxt.js, Tailwind CSS |
| Backend | FastAPI, LangChain (LCEL) |
| AI / LLM | Gemini 2.0 Flash (기본) — Strategy Pattern (OpenAI·Claude 교체 가능) |
| Output Parser | PydanticOutputParser + OutputFixingParser |
| Vector DB | ChromaDB (Gemini embedding-001, 105개 문서) |
| Relational DB | PostgreSQL + SQLAlchemy 2.0 (async) |
| Package Manager | uv (Python), pnpm (Node.js) |
| DevOps | Docker, Docker Compose |

---

## 빠른 시작

```bash
# 저장소 클론
git clone <repo>
cd SajuBon

# 백엔드 실행
cd backend
cp .env.example .env
# .env에 GEMINI_API_KEY, DATABASE_URL 입력

uv sync --group dev

# DB 마이그레이션
uv run alembic upgrade head

# ChromaDB 초기 인덱싱 (최초 1회)
uv run python -c "from rag.ingest import ingest_all; ingest_all()"

# 서버 실행
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API 테스트

```bash
# 이용재 (2001-08-17 양력, 오전 11시생)
curl -X POST http://localhost:8000/api/saju/calc \
  -H "Content-Type: application/json" \
  -d '{"birth_date":"2001-08-17","birth_time":"11:00","gender":"male"}'
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

## 아키텍처

```
Frontend (Vue.js 3 + Nuxt.js)
    │  생년월일시 + 성별 + 고민
    ▼
Backend (FastAPI)
    │
    ├─→ [1] Engine (engine/)
    │         4기둥 · 오행 · 십성 · 신살 · 격국 · 용신 · 대운
    │         behavior_profile · context_ranking · life_domains
    │         ↓
    ├─→ [2] RAG (rag/)
    │         context_ranking + life_domains → ChromaDB 검색
    │         → 명리 해석 텍스트 청크 반환
    │         ↓
    └─→ [3] Writer (llm/)
              calc 데이터 + rag 지식 + 고민
              → 결론형 헤드라인 + 탭 본문 일괄 생성 (PydanticOutputParser)
    ▼
Frontend
    완성된 리포트 전체 수신 → 탭 클릭 시 즉시 전환
```

---

## 코드 구조

```
SajuBon/
├── frontend/               # Vue.js 3 + Nuxt.js 탭 UI → 상세: frontend/README.md
└── backend/                # FastAPI + AI 파이프라인  → 상세: backend/README.md
    ├── main.py
    ├── engine/             # 만세력 계산 엔진
    │   ├── calc/           # 사주·십성·대운·격국·용신 순수 계산
    │   ├── analysis/       # 구조패턴·동역학·시너지·행동프로파일
    │   ├── handlers/       # 기능별 핸들러
    │   └── data/           # 천간·지지·오행·표준시 데이터
    ├── rag/                # ChromaDB 명리학 지식 검색
    │   └── knowledge/      # 60갑자 일주론·십성·신살·구조패턴 JSON
    ├── middleware/         # 요청/응답 로깅 미들웨어
    ├── core/               # 설정·에러코드·커스텀 예외
    ├── llm/                # Writer LLM + 파이프라인
    │   └── pipelines/      # 기능별 파이프라인 (구현 예정)
    ├── routers/            # FastAPI 라우터
    ├── schemas/            # Pydantic 요청/응답 스키마
    ├── db/                 # SQLAlchemy 모델·세션
    └── dependencies/       # FastAPI 의존성
```

---

## 환경변수

`backend/.env.example`을 참고해 `backend/.env`를 작성합니다.

| 변수 | 필수 | 기본값 | 설명 |
|---|---|---|---|
| `LLM_PROVIDER` | — | `gemini` | LLM 선택 (`gemini` \| `openai` \| `claude`) |
| `GEMINI_API_KEY` | gemini 시 필수 | — | Google AI Studio 발급 |
| `OPENAI_API_KEY` | openai 시 필수 | — | OpenAI 플랫폼 발급 |
| `ANTHROPIC_API_KEY` | claude 시 필수 | — | Anthropic Console 발급 |
| `EMBEDDING_PROVIDER` | — | `gemini` | 임베딩 모델 제공사 |
| `CHROMA_PATH` | — | `../mcp-servers/saju-rag/chroma_db` | ChromaDB 경로 |
| `DATABASE_URL` | PostgreSQL 사용 시 필수 | — | `postgresql+asyncpg://user:pw@host:5432/db` |
| `PORT` | — | `8000` | 서버 포트 |

---


## Calc Engine 12단계 파이프라인

`POST /api/saju/calc` 한 번 호출로 순차 실행됩니다.

```
① 4기둥 계산          연·월·일·시주 (진태양시 보정 포함)
② 십성 + 12운성       기둥별 십성·12운성 태그
③ 신살                역마·도화·화개·귀문관살 등 10종
④ 일간 강약           점수화 + level (very_strong/strong/medium/weak/very_weak)
⑤ 격국                월령 + 십성 분포 기반 13종
⑥ 용신                억부 / 조후 / 통관 로직
⑦ 대운                절기 기반 3일=1년 공식 (10구간)
⑧ 음양 비율           8글자 기준
⑨ 구조 패턴           식상생재·관인상생·군겁쟁재 등 15종
   + 동역학            천간합·통근·지지관계·오행흐름
   + 시너지            패턴 × 동역학 교차 (30규칙)
⑩ 행동 프로파일       십성 분포 → behavior_vector 가중 합성
⑪ 컨텍스트 랭킹       패턴·신살 우선순위화 → primary 3 + secondary 2
⑫ 생활 도메인 매핑    career · relationship · wealth · personality 분류
```
