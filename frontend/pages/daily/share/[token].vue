<script setup lang="ts">
import type { DailyFortuneResponse } from '~/types/saju'

const route  = useRoute()
const config = useRuntimeConfig()
const token  = route.params.token as string
const { getDailyShareInput, getDailyFortune } = useSajuApi()

const loading  = ref(true)
const error    = ref('')
const result   = ref<DailyFortuneResponse | null>(null)
const userName = ref('')

// ── 상수 ──────────────────────────────────────────────────────────────────────
const STEMS    = ['갑','을','병','정','무','기','경','신','임','계']
const BRANCHES = ['자','축','인','묘','진','사','오','미','신','유','술','해']
const STEM_HANJA: Record<string,string>   = { '갑':'甲','을':'乙','병':'丙','정':'丁','무':'戊','기':'己','경':'庚','신':'辛','임':'壬','계':'癸' }
const BRANCH_HANJA: Record<string,string> = { '자':'子','축':'丑','인':'寅','묘':'卯','진':'辰','사':'巳','오':'午','미':'未','신':'申','유':'酉','술':'戌','해':'亥' }
const STEM_EL: Record<string,string>   = { '갑':'목','을':'목','병':'화','정':'화','무':'토','기':'토','경':'금','신':'금','임':'수','계':'수' }
const BRANCH_EL: Record<string,string> = { '자':'수','축':'토','인':'목','묘':'목','진':'토','사':'화','오':'화','미':'토','신':'금','유':'금','술':'토','해':'수' }
const CAT_ICON: Record<string,string>  = { exam:'📚', money:'💰', love:'💕', career:'💼', health:'🌿', social:'🤝' }
const CAT_ORDER = ['exam','money','love','career','health','social']
const EL_SWATCH: Record<string,string> = { '목':'var(--el-목)','화':'var(--el-화)','토':'var(--el-토)','금':'var(--el-금)','수':'var(--el-수)' }

// ── 날짜 ──────────────────────────────────────────────────────────────────────
const todayLabel = computed(() => {
  const d = new Date()
  const days = ['일','월','화','수','목','금','토']
  return `${d.getFullYear()}년 ${d.getMonth()+1}월 ${d.getDate()}일 (${days[d.getDay()]})`
})

// ── 계산 ──────────────────────────────────────────────────────────────────────
onMounted(async () => {
  try {
    const share = await getDailyShareInput(token)
    const b = share.birth_input
    userName.value = (b.name as string) || '공유된 사람'
    result.value = await getDailyFortune({
      birth_date:      b.birth_date as string,
      birth_time:      (b.birth_time as string | null) ?? null,
      gender:          (b.gender as 'male' | 'female'),
      calendar:        (b.calendar as 'solar' | 'lunar') ?? 'solar',
      is_leap_month:   (b.is_leap_month as boolean) ?? false,
      birth_longitude: (b.birth_longitude as number | null) ?? undefined,
    })
  } catch {
    error.value = '공유 링크를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
})

// ── 유틸 ──────────────────────────────────────────────────────────────────────
function elColor(el: string) { return el ? `var(--el-${el})` : 'var(--text-secondary)' }
function scoreColor(score: number) {
  if (score >= 80) return 'var(--color-good)'
  if (score >= 60) return 'var(--accent)'
  if (score >= 45) return '#c07818'
  return 'var(--color-bad)'
}

const stemEl   = computed(() => result.value ? STEM_EL[result.value.day_ganji.stem]    ?? '' : '')
const branchEl = computed(() => result.value ? BRANCH_EL[result.value.day_ganji.branch] ?? '' : '')
const orderedFortunes = computed(() => {
  if (!result.value) return []
  return CAT_ORDER.map(k => ({ key: k, ...result.value!.fortunes[k] }))
})

// ── SEO ───────────────────────────────────────────────────────────────────────
useSeoMeta({
  title:         () => result.value ? `${userName.value}님의 오늘의 운세 보러가기` : '오늘의 운세 보러가기',
  ogTitle:       () => result.value ? `${userName.value}님의 오늘의 운세 보러가기` : '오늘의 운세 보러가기',
  description:   () => result.value ? `${userName.value}님의 오늘 운세를 확인해보세요.` : '사주구리에서 오늘의 운세를 확인해보세요.',
  ogDescription: () => result.value ? `${userName.value}님의 오늘 운세를 확인해보세요.` : '사주구리에서 오늘의 운세를 확인해보세요.',
  ogImage:       `${config.public.siteUrl}/onboarding-illust.png`,
  ogUrl:         `${config.public.siteUrl}/daily/share/${token}`,
})
</script>

<template>
  <div class="share-wrap">

    <!-- 헤더 -->
    <div class="share-header">
      <NuxtLink to="/daily" class="back-btn">
        <svg viewBox="0 0 24 24" fill="none" class="w-5 h-5">
          <path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </NuxtLink>
      <div>
        <h1 class="share-title">
          <template v-if="!loading && result">{{ userName }}님의 오늘의 운세</template>
          <template v-else>오늘의 운세</template>
        </h1>
        <p class="share-date fs-sub">{{ todayLabel }}</p>
      </div>
    </div>

    <!-- 로딩 -->
    <div v-if="loading" class="center-state">
      <svg class="animate-spin w-8 h-8" viewBox="0 0 40 40" fill="none">
        <circle cx="20" cy="20" r="17" stroke="var(--border-subtle)" stroke-width="3"/>
        <path d="M20 3a17 17 0 0 1 17 17" stroke="var(--accent)" stroke-width="3" stroke-linecap="round"/>
      </svg>
      <p class="fs-sub" style="color:var(--text-muted);margin-top:12px;">운세 계산 중…</p>
    </div>

    <!-- 에러 -->
    <div v-else-if="error" class="card" style="text-align:center;padding:32px;">
      <p class="fs-body" style="color:var(--color-bad);">{{ error }}</p>
      <NuxtLink to="/daily" class="btn-primary" style="margin-top:16px;max-width:200px;margin-inline:auto;">
        내 운세 보기
      </NuxtLink>
    </div>

    <!-- 결과 -->
    <template v-else-if="result">

      <!-- 요약 카드 -->
      <div class="card summary-card">
        <div class="summary-top">
          <div class="summary-ganji">
            <span class="ganji ganji-char" :style="`color:${elColor(stemEl)}`">{{ STEM_HANJA[result.day_ganji.stem] }}</span>
            <span class="ganji ganji-char" :style="`color:${elColor(branchEl)}`">{{ BRANCH_HANJA[result.day_ganji.branch] }}</span>
          </div>
          <p class="overall-text fs-body">{{ result.overall }}</p>
        </div>
        <div class="basis-row">
          <span class="basis-label fs-tiny">📌 오늘의 근거</span>
          <span class="basis-text fs-tiny">{{ result.basis }}</span>
        </div>
      </div>

      <!-- 옷 색깔 + 조심 -->
      <div class="info-row">
        <div class="card info-card">
          <div class="info-icon-row">
            <div v-if="result.clothing_color.element" class="el-swatch"
              :style="`background:${EL_SWATCH[result.clothing_color.element] ?? 'var(--surface-3)'}`" />
            <span class="fs-label" style="font-weight:700;color:var(--text-primary);">오늘의 옷 색깔</span>
          </div>
          <p class="info-value fs-body">{{ result.clothing_color.color }}</p>
          <p class="info-reason fs-tiny">{{ result.clothing_color.reason }}</p>
        </div>
        <div class="card info-card caution-card">
          <div class="info-icon-row">
            <span class="caution-icon">⚠️</span>
            <span class="fs-label" style="font-weight:700;color:var(--color-bad);">오늘 조심</span>
          </div>
          <p class="info-value fs-sub caution-text">{{ result.caution }}</p>
        </div>
      </div>

      <!-- 카테고리 운세 -->
      <div class="fortunes-list">
        <div v-for="item in orderedFortunes" :key="item.key" class="card fortune-card">
          <div class="fortune-top">
            <div class="fortune-header">
              <span class="fortune-icon">{{ CAT_ICON[item.key] }}</span>
              <span class="fortune-label fs-body">{{ item.label }}</span>
            </div>
            <div class="fortune-score-col">
              <span class="score-num" :style="`color:${scoreColor(item.score)}`">{{ item.score }}</span>
              <span class="fs-tiny" style="color:var(--text-muted);">/100</span>
            </div>
          </div>
          <div class="score-bar-row">
            <div class="score-bar-track">
              <div class="score-bar-fill" :style="`width:${item.score}%;background:${scoreColor(item.score)}`" />
            </div>
            <span class="level-badge fs-tiny" :style="`color:${scoreColor(item.score)}`">{{ item.level }}</span>
          </div>
          <p class="fortune-text fs-sub">{{ item.text }}</p>
        </div>
      </div>

      <!-- 내 운세 보기 CTA -->
      <NuxtLink to="/daily" class="btn-primary" style="text-align:center;margin-top:4px;">
        내 운세 보기
      </NuxtLink>

    </template>
  </div>
</template>

<style scoped>
.share-wrap {
  max-width: 480px;
  margin: 0 auto;
  padding: 12px 20px 60px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.share-header {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding-top: 8px;
}
.back-btn {
  display: flex; align-items: center; justify-content: center;
  width: 32px; height: 32px;
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
  background: var(--surface-1);
  color: var(--text-secondary);
  flex-shrink: 0; margin-top: 2px;
}
.share-title {
  font-size: 22px; font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em; line-height: 1.2;
}
.share-date { color: var(--text-muted); margin-top: 3px; }
.center-state {
  min-height: 300px;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
}
.summary-card { display: flex; flex-direction: column; gap: 12px; }
.summary-top { display: flex; align-items: center; gap: 16px; }
.summary-ganji { display: flex; gap: 0; flex-shrink: 0; line-height: 1; }
.ganji-char { font-size: 52px; font-weight: 700; font-family: var(--font-ganji); letter-spacing: -0.02em; }
.overall-text { flex: 1; min-width: 0; color: var(--text-primary); font-weight: 500; line-height: 1.65; }
.basis-row {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 10px 12px; border-radius: 10px;
  background: var(--surface-2); border: 1px solid var(--border-subtle); flex-wrap: wrap;
}
.basis-label { font-weight: 700; color: var(--text-muted); white-space: nowrap; }
.basis-text { color: var(--text-secondary); line-height: 1.5; }
.info-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.info-card { display: flex; flex-direction: column; gap: 6px; padding: 14px 16px; }
.info-icon-row { display: flex; align-items: center; gap: 6px; }
.el-swatch { width: 14px; height: 14px; border-radius: 3px; flex-shrink: 0; }
.caution-icon { font-size: 14px; }
.info-value { font-weight: 600; color: var(--text-primary); line-height: 1.4; }
.info-reason { color: var(--text-muted); line-height: 1.5; }
.caution-card .caution-text { color: var(--text-secondary); font-weight: 400; font-size: var(--fs-tiny); line-height: 1.55; }
.fortunes-list { display: flex; flex-direction: column; gap: 10px; }
.fortune-card { display: flex; flex-direction: column; gap: 8px; }
.fortune-top { display: flex; align-items: center; justify-content: space-between; }
.fortune-header { display: flex; align-items: center; gap: 8px; }
.fortune-icon { font-size: var(--fs-body); line-height: 1; }
.fortune-label { font-weight: 700; color: var(--text-primary); }
.fortune-score-col { display: flex; align-items: baseline; gap: 2px; flex-shrink: 0; }
.score-num { font-size: 26px; font-weight: 800; line-height: 1; font-variant-numeric: tabular-nums; }
.score-bar-row { display: flex; align-items: center; gap: 8px; }
.score-bar-track { flex: 1; height: 4px; border-radius: 2px; background: var(--border-subtle); overflow: hidden; }
.score-bar-fill { height: 100%; border-radius: 2px; }
.level-badge { font-weight: 600; white-space: nowrap; }
.fortune-text { color: var(--text-secondary); line-height: 1.7; }

@media (min-width: 768px) {
  .share-wrap { max-width: 960px; padding: 32px 40px 60px; gap: 20px; }
  .ganji-char { font-size: 64px; }
  .fortunes-list { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
}
</style>
