<script setup lang="ts">
const props = defineProps<{
  error: { statusCode: number; statusMessage?: string }
}>()

const is500 = computed(() => props.error.statusCode >= 500)

function goHome() {
  clearError({ redirect: '/' })
}
</script>

<template>
  <div class="error-root">
    <div class="error-card">
      <!-- 로고 -->
      <NuxtLink to="/" class="error-logo ganji" @click.prevent="goHome">
        <span style="color: var(--text-primary);">사주</span><span style="color: var(--accent);">구리</span>
      </NuxtLink>

      <!-- 코드 -->
      <p class="error-code">{{ error.statusCode }}</p>

      <!-- 메시지 -->
      <h1 class="error-title">{{ is500 ? '일시적인 오류가 발생했어요' : '페이지를 찾을 수 없어요' }}</h1>
      <p class="error-sub">{{ is500 ? '잠시 후 다시 시도해 주세요.' : '존재하지 않거나 삭제된 페이지입니다.' }}</p>

      <!-- 홈 버튼 -->
      <button class="btn-primary error-btn" @click="goHome">
        홈으로 돌아가기
      </button>
    </div>
  </div>
</template>

<style scoped>
.error-root {
  /* CSS 변수 fallback — app.vue 레이아웃 없이 렌더되므로 여기서 선언 (전역 :root 오염 방지) */
  --bg-base:        #0f0e0d;
  --surface-1:      #1a1916;
  --border-default: rgba(255,255,255,0.1);
  --text-primary:   #f0ede8;
  --text-muted:     #7a756e;
  --accent:         #c9833a;
  --font-ganji:     'Joseon100Years', 'Noto Serif KR', Georgia, serif;
  --fs-body:        0.9375rem;
  --fs-sub:         0.8125rem;
  min-height: 100dvh;
  background: var(--bg-base);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.error-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  max-width: 360px;
  width: 100%;
  padding: 48px 32px;
  background: var(--surface-1);
  border: 1px solid var(--border-default);
  border-radius: 24px;
  text-align: center;
}

.error-logo {
  font-family: var(--font-ganji);
  font-size: 1.2rem;
  font-weight: 700;
  text-decoration: none;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

.error-code {
  font-size: 4rem;
  font-weight: 900;
  color: var(--accent);
  line-height: 1;
  margin: 0;
  letter-spacing: -0.02em;
}

.error-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.4;
}

.error-sub {
  font-size: var(--fs-sub);
  color: var(--text-muted);
  margin: 0 0 8px;
  line-height: 1.6;
}

.error-btn {
  margin-top: 4px;
  width: 100%;
  max-width: 200px;
  padding: 13px 24px;
  cursor: pointer;
}
</style>
