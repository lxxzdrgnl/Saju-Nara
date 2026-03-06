# Backend - FastAPI AI Agent 서버

AI Agent 오케스트레이션 서버. MCP 도구를 활용해 사주 분석 리포트를 생성합니다.

---

## 역할

```
사용자 요청 수신
    │
    ├─→ Planner Agent (GPT-4o)
    │     ├─ saju-calc MCP 호출 → 4기둥/신살/격국/용신
    │     └─ 10개 결론형 헤드라인 생성
    │
    │ [탭 클릭]
    └─→ Writer Agent (Claude Sonnet)
          ├─ saju-rag MCP 호출 → 관련 명리 지식
          └─ SSE 스트리밍 리포트 생성
```

---

## 기술 스택

| 항목 | 기술 |
|---|---|
| Framework | FastAPI |
| Agent | LangChain / LangGraph |
| LLM | GPT-4o (Planner), Claude Sonnet (Writer) |
| Streaming | Server-Sent Events (SSE) |
| MCP Client | MCP SDK (Python) |

---

## 구현 예정

> 현재 MCP 서버 구현 완료 후 진행 예정
