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

## 핵심 컨셉: Headline-Driven Insights

사주 계산 결과와 사용자의 실제 고민을 AI가 교차 분석해 **오직 당신만을 위한 결론형 탭 리포트**를 생성합니다.

```
입력: "1990-03-15 14:30 남성 + 회사 상사와 갈등이 심해 이직을 고민 중입니다"

출력:
  탭 1. 기묘일주, 부드러운 겉모습 아래 타협 불가한 고집이 상사의 권위와 충돌
  탭 2. 올해 역마살 + 현재 대운 변화기 — 이직은 선택이 아닌 운명의 수순
  탭 3. 용신 수(水)의 기운이 강한 IT·금융 계열에서 진가를 발휘할 팔자
  탭 4. 칠살격의 추진력이 직장 내 갈등을 연료 삼아 성장을 가속
  ...
```

> **UX 원칙**: 모든 탭 내용은 한 번에 생성됩니다. 탭 클릭은 단순 뷰 전환 — 추가 API 호출 없음.

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

Engine과 RAG는 **Python 라이브러리로 직접 임포트** — 네트워크 오버헤드 없음.

---

## 4가지 기능

| 기능 | 엔드포인트 | 파이프라인 |
|---|---|---|
| 사주 정밀 분석 | `POST /api/saju/calc` | Engine → RAG → Context Filter → Writer |
| 궁합 | `POST /api/compatibility` | Engine×2 → Synastry → RAG → Writer |
| 오늘의 운세 | `POST /api/daily` | Engine + 오늘간지 → Daily Tags → RAG → Writer |
| 한줄 상담 | `POST /api/question` | Engine → 가중 RAG 검색 → Writer |

---

## 코드 구조

```
SajuBon/
├── frontend/               # Vue.js 3 + Nuxt.js 탭 UI (구현 예정)
└── backend/                # FastAPI + AI 파이프라인
    ├── main.py
    ├── pyproject.toml
    ├── engine/             # 만세력 계산 엔진
    │   ├── calc/           # 사주·십성·대운·격국·용신 순수 계산
    │   ├── analysis/       # 구조패턴·동역학·시너지·행동프로파일 분석
    │   ├── handlers/       # 기능별 핸들러 (계산 파이프라인 조합)
    │   └── data/           # 천간·지지·오행·역사적 표준시 데이터
    ├── rag/                # ChromaDB 기반 명리학 지식 검색
    │   └── knowledge/      # 60갑자 일주론·십성·신살·구조패턴·오행 JSON
    ├── llm/                # Writer LLM (구현 예정)
    ├── pipelines/          # 기능별 파이프라인 (구현 예정)
    ├── routers/            # FastAPI 라우터
    ├── schemas/            # Pydantic 요청/응답 스키마
    ├── db/                 # SQLAlchemy 모델·세션
    ├── core/               # 앱 설정 (pydantic-settings)
    └── dependencies/       # FastAPI 의존성 (auth·db session)
```

---

## Calc Engine 12단계 파이프라인

`POST /api/saju/calc` 한 번 호출로 순차 실행됩니다.

```
① 4기둥 계산          연·월·일·시주 (진태양시 보정 포함)
② 십성 + 12운성       기둥별 십성·12운성 태그
③ 신살                역마·도화·화개·귀문관살 등 10종
④ 일간 강약           점수화 + level (strong/medium/weak)
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

## 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python 3.10+, TypeScript |
| Frontend | Vue.js 3, Pinia, Nuxt.js, Tailwind CSS |
| Backend | FastAPI, LangChain (LCEL) |
| AI / LLM | Gemini (기본) — Strategy Pattern (OpenAI·Claude 교체 가능) |
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

# 백엔드 실행
cd backend
cp .env.example .env
# GEMINI_API_KEY=..., DATABASE_URL=... 입력

uv sync --group dev
uv run uvicorn main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)
```

### API 테스트

```bash
curl -X POST http://localhost:8000/api/saju/calc \
  -H "Content-Type: application/json" \
  -d '{"birth_date":"1990-03-15","birth_time":"14:30","gender":"male"}'
```
