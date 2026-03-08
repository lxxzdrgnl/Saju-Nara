# Saju-RAG MCP

명리학 **지식 베이스 RAG** MCP 서버.

saju-calc가 생성한 `behavior_profile` · `life_domains` · `context_ranking`을 쿼리 seed로 받아,
ChromaDB에서 관련 해석 텍스트를 검색해 Writer Agent에 전달합니다.

---

## 설계 원칙

- **해석만, 계산 없음**: saju-calc의 구조 데이터를 받아 관련 지식을 검색
- **RAG 기반**: ChromaDB 시맨틱 검색 + 메타 필터 조합
- **도메인 분리 검색**: life_domains 4개 영역(career·relationship·wealth·personality)별 독립 쿼리
- **근거 있는 해석**: Writer가 생성하는 모든 문장은 지식 베이스 청크에 기반

---

## 지식 베이스 구성

| 파일 | 항목 수 | 핵심 필드 | 용도 |
|---|---|---|---|
| `wuxing.json` | 5개 (목·화·토·금·수) | `personality_vector`, `behavior_vector`, `interaction_logic`, `engine_tags` | 오행 에너지 → 성격 변환 |
| `ten_gods.json` | 10개 (비견~정인) | `behavior_vector`, `life_patterns`, `decision_style`, `consulting_points` | 십성 → 행동 패턴·상담 |
| `sin_sal.json` | 10종 | `priority`(int), `pillar_nuance`, `consulting_tip`, `activation_rule` | 신살 해석 + 조언 |
| `structure_patterns.json` | 7종 | `flow.type`, `career_hint`, `engine_tags`, `interpretation_tags` | 구조 패턴 해석 |
| `dynamics.json` | 14개 | `trigger`, `traits`, `career_vibe`, `pattern_synergy` | 동역학 해석 (천간합·통근 등) |
| `ilju.json` | 60개 (60갑자) | 일주별 성격·직업·연애 특징 | 일주론 전문 해석 |

---

## RAG 스키마 설계 원칙

모든 지식 파일은 공통 필드 구조를 따릅니다.

```
engine_tags       : 계산 엔진용 구조적 태그 (검색 필터·패턴 매칭)
interpretation_tags: Writer용 해석 힌트 태그 (컨설팅 언어)
embedding_context : 벡터 임베딩 기준 텍스트 (한국어 문맥)
```

---

## saju-calc → saju-rag 데이터 흐름

```
saju-calc 출력
  ├── behavior_profile   ["rule_adherence", "competitive_drive", ...]
  ├── life_domains       { career: [...], relationship: [...], ... }
  └── context_ranking    { primary_context: [...], secondary_context: [...] }
            │
            ▼
saju-rag RAG 쿼리 구성
  ├── 도메인별 쿼리     life_domains.career → ten_gods + structure_patterns 검색
  ├── 컨텍스트 쿼리     primary_context 항목 → sin_sal + dynamics 검색
  └── 일주 쿼리         day_pillar 간지 → ilju.json 검색
            │
            ▼
Writer Agent
  각 탭의 life_domain에 맞는 청크 + 컨텍스트 청크 전달
  → 근거 있는 해석 문장 생성
```

---

## 프로젝트 구조

```
saju-rag/
├── main.py                # FastMCP 서버 진입점
├── pyproject.toml
├── .env.example
├── knowledge/             # JSON 지식 파일 (ChromaDB 인덱싱 원본)
│   ├── wuxing.json        # 오행 5개
│   ├── ten_gods.json      # 십성 10개
│   ├── sin_sal.json       # 신살 10종
│   ├── structure_patterns.json  # 구조 패턴 7종
│   ├── dynamics.json      # 동역학 14개
│   └── ilju.json          # 60갑자 일주론
├── lib/
│   ├── embedder.py        # ChromaDB 임베딩·인덱싱
│   ├── retriever.py       # 시맨틱 검색 + 메타 필터
│   └── query_builder.py   # saju-calc 출력 → RAG 쿼리 변환
└── tools/
    ├── search_knowledge.py       # 범용 지식 검색 tool
    ├── search_by_life_domain.py  # 도메인별 검색 tool
    └── search_ilju.py            # 일주론 검색 tool
```

---

## 실행

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

cd mcp-servers/saju-rag
cp .env.example .env
# OPENAI_API_KEY 입력 (임베딩용)

uv sync --group dev

# MCP Inspector
DANGEROUSLY_OMIT_AUTH=true uv run fastmcp dev inspector main.py

# Docker
docker compose up saju-rag
```

---

## 구현 예정

> saju-calc 구현 완료 후 진행 예정.
> 지식 파일(knowledge/) 스키마 설계는 완료되어 있습니다.
