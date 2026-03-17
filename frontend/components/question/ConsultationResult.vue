<script setup lang="ts">
const CATEGORY_LABELS: Record<string, string> = {
  career: '직업·이직',
  love:   '연애·결혼',
  money:  '재물·투자',
  health: '건강',
  general: '기타',
}

const SIJIN = [
  { ko: '자시', hanja: '子時' }, { ko: '축시', hanja: '丑時' },
  { ko: '인시', hanja: '寅時' }, { ko: '묘시', hanja: '卯時' },
  { ko: '진시', hanja: '辰時' }, { ko: '사시', hanja: '巳時' },
  { ko: '오시', hanja: '午時' }, { ko: '미시', hanja: '未時' },
  { ko: '신시', hanja: '申時' }, { ko: '유시', hanja: '酉時' },
  { ko: '술시', hanja: '戌時' }, { ko: '해시', hanja: '亥時' },
]

const props = defineProps<{
  question:  string
  headline:  string
  content:   string
  category:  string
  name?:     string | null
  birthDate?: string | null
  birthTime?: string | null
  gender?:   string | null
  createdAt?: string | null
}>()

function birthTimeLabel(time: string | null | undefined): string {
  if (!time) return '시간 모름'
  const [h] = time.split(':').map(Number)
  const idx = h === 23 ? 0 : Math.floor(((h + 1) % 24) / 2)
  const s = SIJIN[idx]
  return s ? `${s.ko}(${s.hanja})` : time
}

function formatDate(iso: string) {
  const d = new Date(iso)
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
}

const hasProfile = computed(() => props.name || props.birthDate)
</script>

<template>
  <!-- 사용자 정보 블록 -->
  <div v-if="hasProfile" class="profile-card card">
    <div class="profile-avatar">
      <img src="/profile-illust.webp" alt="" class="avatar-img" />
    </div>
    <div class="profile-info">
      <span v-if="name" class="profile-name">{{ name }}</span>
      <span v-if="birthDate" class="profile-birth">
        {{ birthDate.replace(/-/g, '.') }}
        <template v-if="gender"> · {{ gender === 'male' ? '남' : '여' }}</template>
        · {{ birthTimeLabel(birthTime) }}
      </span>
    </div>
  </div>

  <!-- 질문 + 답변 블록 -->
  <div class="qa-card card">
    <!-- 질문 섹션 -->
    <div class="qa-question-section">
      <span v-if="name" class="qa-label">{{ name }} 님의 고민</span>
      <p class="qa-question">{{ question }}</p>
    </div>

    <div class="qa-divider" />

    <!-- 답변 섹션 -->
    <div class="qa-answer-section">
      <div class="qa-meta">
        <span class="qa-category">{{ CATEGORY_LABELS[category] ?? category }}</span>
        <span v-if="createdAt" class="qa-date">{{ formatDate(createdAt) }}</span>
      </div>
      <h2 class="qa-headline">{{ headline }}</h2>
      <p class="qa-content">{{ content }}</p>
    </div>
  </div>
</template>

<style scoped>
/* 사용자 정보 블록 */
.profile-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
}
.profile-avatar {
  width: 52px; height: 52px;
  border-radius: 14px;
  overflow: hidden;
  flex-shrink: 0;
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; }
.profile-info { display: flex; flex-direction: column; gap: 2px; }
.profile-name  { font-size: 14px; font-weight: 700; color: var(--text-primary); }
.profile-birth { font-size: 12px; color: var(--text-muted); }

/* 질문 + 답변 블록 */
.qa-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
}

.qa-question-section {
  padding: 20px 20px 18px;
  display: flex; flex-direction: column; gap: 6px;
}
.qa-label {
  font-size: 11px; font-weight: 700;
  color: var(--accent);
  letter-spacing: 0.03em;
}
.qa-question {
  font-size: 16px; font-weight: 400;
  color: var(--text-primary); line-height: 1.65;
  letter-spacing: -0.01em;
}

.qa-divider {
  height: 1px;
  background: var(--border-subtle);
  margin: 0 20px;
}

.qa-answer-section {
  padding: 18px 20px 22px;
  display: flex; flex-direction: column; gap: 8px;
}
.qa-meta {
  display: flex; justify-content: space-between; align-items: center;
}
.qa-category {
  font-size: 11px; font-weight: 700;
  color: var(--accent); text-transform: uppercase; letter-spacing: 0.06em;
}
.qa-date { font-size: 11px; color: var(--text-muted); }
.qa-headline {
  font-size: 16px; font-weight: 800;
  color: var(--text-primary); line-height: 1.5; letter-spacing: -0.01em;
}
.qa-content {
  font-size: var(--fs-body); color: var(--text-secondary);
  line-height: 1.75; white-space: pre-wrap;
}
</style>
