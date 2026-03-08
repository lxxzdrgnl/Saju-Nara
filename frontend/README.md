# Frontend — Vue.js 3 웹앱

사용자 입력 수신 및 AI가 생성한 사주 리포트를 탭 UI로 렌더링하는 웹 애플리케이션입니다.

---

## UX 원칙

```
[생년월일시 + 고민 입력]
        │
        ▼ [분석 중... 로딩]
Backend → 10개 탭 전체 리포트 일괄 수신
        │
        ▼
탭 1 | 탭 2 | 탭 3 | ... | 탭 10
  클릭 시 즉시 전환 (추가 API 없음)
```

탭 클릭은 단순 뷰 전환입니다. 추가 네트워크 요청 없이 이미 완성된 데이터를 즉시 표시합니다.

---

## 핵심 컴포넌트

| 컴포넌트 | 역할 |
|---|---|
| `DynamicInputForm` | 생년월일시·음양력·성별·고민 입력 수집 |
| `LoadingState` | 리포트 생성 중 로딩 표시 (최초 1회) |
| `HeadlineTabBar` | AI가 생성한 10개 결론형 헤드라인을 탭으로 표시 |
| `TabContentViewer` | 선택된 탭의 완성된 상세 내용 즉시 렌더링 |

---

## 기술 스택

| 항목 | 기술 |
|---|---|
| Framework | Vue.js 3 + Nuxt.js |
| 상태관리 | Pinia |
| 스타일 | Tailwind CSS |
| 언어 | TypeScript |

---

## 실행

```bash
pnpm install

# 개발 서버
pnpm dev
# → http://localhost:3000

# Docker
docker compose up frontend
```

---

## 구현 예정

> Backend 구현 완료 후 진행 예정.
