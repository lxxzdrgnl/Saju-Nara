# Backend — FastAPI AI Agent 서버

AI Agent 오케스트레이션 서버. saju-calc / saju-rag MCP를 활용해 사주 분석 리포트를 일괄 생성합니다.

---

## 역할

```
POST /report  { birth_date, birth_time, gender, calendar, concern }
        │
        ├─→ [1] saju-calc MCP  →  calculate_saju()
        │         4기둥·오행·십성·신살·격국·용신
        │         + behavior_profile / context_ranking / life_domains
        │                     ↓
        ├─→ [2] saju-rag MCP
        │         context_ranking + life_domains → RAG 쿼리
        │         → 관련 명리 해석 텍스트 청크 반환
        │                     ↓
        └─→ [3] Writer Agent (GPT-4o)
                  calc 데이터 + rag 청크 + 사용자 고민
                  → 10개 결론형 헤드라인 + 탭 내용 일괄 집필
        │
        ▼
{ headlines: [...], tabs: { "탭제목": "내용", ... } }  (완성된 JSON 1회 반환)
```

> **UX 원칙**: 탭 클릭은 단순 뷰 전환. 추가 API 호출 없음. 로딩은 최초 1회.

---

## Writer Agent 역할

calc + RAG 결과를 받아 헤드라인 기획부터 탭 내용 집필까지 일괄 수행합니다.

```python
# Writer 입력
{
  "concern": "회사 상사와 갈등이 심해 이직을 고민 중입니다",
  "calc": {
    "day_pillar": "경오",
    "behavior_profile": ["rule_adherence", "competitive_drive", ...],
    "life_domains": {
      "career": ["rule_adherence", "institutional_growth", "sharp_expression"],
      ...
    },
    "context_ranking": {
      "primary_context": [{ "id": "gwan_in_sang_saeng", ... }],
      ...
    },
    "synergy_tags": ["analytical_humor_defense", ...]
  },
  "rag_chunks": [
    "경오일주: 목표를 향해 질주하는 백마...",
    "관인상생: 조직이 역량을 키우는 선순환 구조...",
    ...
  ]
}

# Writer 출력
{
  "headlines": [
    "경오일주, 강한 자존심이 상사의 권위와 정면 충돌하는 형국",
    "올해 역마살이 터지는 해 — 이직은 선택이 아닌 운명의 수순",
    ...
  ],
  "tabs": {
    "경오일주, 강한 자존심이...": "당신의 일간 경금(庚金)은...",
    ...
  }
}
```

---

## RAG 쿼리 구성

context_ranking과 life_domains가 RAG 쿼리 seed 역할을 합니다.

```python
# saju-rag MCP에 전달되는 쿼리 예
queries = {
  "career":       life_domains["career"],        # ["rule_adherence", ...]
  "personality":  life_domains["personality"],
  "primary":      context_ranking["primary_context"],  # 구조 패턴·신살
  "ilju":         day_pillar,                    # "경오"
}
```

---

## 기술 스택

| 항목 | 기술 |
|---|---|
| Framework | FastAPI |
| Agent | LangChain / LangGraph |
| LLM | GPT-4o (Writer) |
| MCP Client | MCP SDK (Python) |
| DB | PostgreSQL (상담 이력) |

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|---|---|---|
| `POST` | `/report` | 사주 분석 리포트 일괄 생성 |
| `POST` | `/compatibility` | 두 사람 궁합 리포트 |
| `GET` | `/history/{user_id}` | 과거 상담 이력 |

---

## 실행

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

cd backend
cp .env.example .env
# OPENAI_API_KEY, DATABASE_URL, SAJU_CALC_URL, SAJU_RAG_URL 입력

uv sync --group dev

uv run uvicorn main:app --reload
# → http://localhost:8000

docker compose up backend
```

---

## 구현 예정

> MCP 서버 구현 완료 후 진행 예정.
