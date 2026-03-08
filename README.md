# SajuNara

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3.0-4FC08D?style=flat-square&logo=vue.js&logoColor=white)
![Nuxt](https://img.shields.io/badge/Nuxt.js-3.0-00DC82?style=flat-square&logo=nuxt.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![GPT-4o](https://img.shields.io/badge/GPT--4o-Planner+Writer-412991?style=flat-square&logo=openai&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-FF6B35?style=flat-square)
![MCP](https://img.shields.io/badge/MCP-3_Tier_Agent-black?style=flat-square)

**AI가 당신의 사주(四柱)와 오늘의 고민을 함께 읽어드립니다.**

> "재물운" (X)
> "30대 중반, 바위 틈에서 물이 솟구치듯 재물이 터질 팔자" (O)

---

## 아키텍처

MCP(Model Context Protocol)로 **계산 엔진**과 **해석 지식베이스**를 분리한 3-Tier 구조입니다.

### 요청 흐름

```
Frontend (Vue.js)
    │  생년월일시 + 성별 + 고민
    ▼
Backend (FastAPI)
    │
    ├─→ [1] saju-calc MCP
    │         4기둥 · 오행 · 십성 · 신살 · 격국 · 용신 계산
    │         behavior_profile / context_ranking / life_domains 합성
    │         ↓
    ├─→ [2] saju-rag MCP
    │         context_ranking + life_domains → RAG 쿼리
    │         → 관련 명리 해석 텍스트 청크 반환
    │         ↓
    └─→ [3] Writer Agent (GPT-4o)
              calc 데이터 + rag 지식 + 고민
              → 10개 결론형 헤드라인 + 탭 내용 일괄 생성
    ▼
Frontend
    완성된 리포트 전체 수신 → 탭 클릭 시 즉시 전환 (추가 API 없음)
```

> **UX 원칙**: 탭 클릭은 단순 뷰 전환입니다. 로딩은 리포트 최초 생성 시 1회만 발생합니다.

---

## 코드 구조

| 레이어 | 경로 | 역할 |
|---|---|---|
| Frontend | [frontend/](./frontend) | Vue.js 3 + Nuxt.js 탭 UI |
| Backend | [backend/](./backend) | FastAPI + AI Agent 오케스트레이션 |
| Saju-Calc MCP | [mcp-servers/saju-calc/](./mcp-servers/saju-calc) | 만세력 계산 엔진 |
| Saju-RAG MCP | [mcp-servers/saju-rag/](./mcp-servers/saju-rag) | 명리학 지식 RAG |

---

## Calc Engine 내부 파이프라인

`calculate_saju` 한 번 호출로 12단계 파이프라인이 순차 실행됩니다.

```
① 4기둥 계산          연·월·일·시주 (진태양시 보정 포함)
② 십성 + 12운성       기둥별 십성·12운성 태그
③ 신살                역마·도화·귀문관살 등 10종
④ 일간 강약           점수화 + level(very_weak~very_strong)
⑤ 격국                월령 + 십성 분포 기반 13종
⑥ 용신                억부 / 조후 / 통관 로직
⑦ 대운                절기 기반 3일=1년 공식
⑧ 음양 비율           8글자 기준
⑨ 구조 패턴           식상생재·관인상생·군겁쟁재 등 15종 (종격 포함)
   + 동역학            천간합·통근·지지관계·오행흐름
   + 시너지            패턴 × 동역학 교차 (30규칙)
⑩ 행동 프로파일       십성 분포 → behavior_vector 가중 합성
⑪ 컨텍스트 랭킹       패턴·신살 우선순위화 → primary 3 + secondary 2
⑫ 생활 도메인 매핑    career · relationship · wealth · personality 분류
```

---

## 핵심 컨셉: Headline-Driven Insights

AI가 사주 계산 결과와 지금 이 순간의 고민을 함께 분석해 **오직 당신만을 위한 결론형 헤드라인**을 생성합니다.

```
입력: 생년월일시 + "회사 상사와 갈등이 심해 이직을 고민 중입니다"

출력:
  탭 1. 경오일주, 강한 자존심이 상사의 권위와 정면 충돌하는 형국
  탭 2. 올해 역마살이 터지는 해 — 이직은 선택이 아닌 운명의 수순
  탭 3. 용신 화(火)의 기운이 강한 남쪽 계열 회사에서 빛을 발할 팔자
  탭 4. 월주 계묘, 동료보다 상사와의 관계에서 더 많이 소모되는 구조
  ...
```

---

## 사주팔자(四柱八字)란?

태어난 **연·월·일·시** 네 기둥(四柱), 여덟 글자(八字)로 이루어진 동양 명리학의 핵심입니다.

| 기둥 | 의미 |
|---|---|
| 연주(年柱) | 조상·초년운 (0~15세) |
| 월주(月柱) | 부모·청년운 (16~30세) |
| 일주(日柱) | 자신·배우자·중년운 (31~45세) |
| 시주(時柱) | 자녀·말년운 (46세~) |

---

## 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python 3.10+, TypeScript |
| Frontend | Vue.js 3, Pinia, Nuxt.js, Tailwind CSS |
| Backend | FastAPI, LangChain / LangGraph, MCP SDK |
| AI / LLM | GPT-4o (Planner + Writer) |
| Database | ChromaDB (Vector DB), PostgreSQL (이력) |
| Package Manager | uv (Python), pnpm (Node.js) |
| DevOps | Docker, Docker Compose, MCP Inspector |

---

## 빠른 시작

### Docker (전체 스택)

```bash
cp .env.example .env
# OPENAI_API_KEY, DATABASE_URL 입력

docker compose up -d

# 서비스 포트
#   frontend   → http://localhost:3000
#   backend    → http://localhost:8000
#   saju-calc  → http://localhost:8001
#   saju-rag   → http://localhost:8002
```

### 로컬 개발 (saju-calc MCP)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

cd mcp-servers/saju-calc
uv sync --group dev

# MCP Inspector
DANGEROUSLY_OMIT_AUTH=true uv run fastmcp dev inspector main.py
# → http://localhost:6274

uv run pytest tests/
```
