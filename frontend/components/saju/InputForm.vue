<script setup lang="ts">
import type { SajuCalcRequest } from '~/types/saju'
import {
  searchCities, calcSolarCorrection, formatCorrection, SEOUL_CORRECTION, type CityOption,
} from '~/utils/citySearch'

const emit = defineEmits<{ submit: [req: SajuCalcRequest] }>()

const form = reactive({
  name: '',
  birth_date: '',
  birth_time: '12:00',
  gender: 'male' as 'male' | 'female',
  calendar: 'solar' as 'solar' | 'lunar',
  is_leap_month: false,
})

// ── 날짜 분리 입력 ──────────────────────────────────────────────────
const yearRef  = ref<HTMLInputElement | null>(null)
const monthRef = ref<HTMLInputElement | null>(null)
const dayRef   = ref<HTMLInputElement | null>(null)
const yearVal  = ref('')
const monthVal = ref('')
const dayVal   = ref('')

watch([yearVal, monthVal, dayVal], () => {
  const y = yearVal.value
  const m = monthVal.value.padStart(2, '0')
  const d = dayVal.value.padStart(2, '0')
  form.birth_date = (y.length === 4 && monthVal.value && dayVal.value)
    ? `${y}-${m}-${d}` : ''
})

function onYearInput(e: Event) {
  const el = e.target as HTMLInputElement
  const val = el.value.replace(/\D/g, '').slice(0, 4)
  yearVal.value = val; el.value = val
  if (val.length === 4) monthRef.value?.focus()
}

function onMonthInput(e: Event) {
  const el = e.target as HTMLInputElement
  let val = el.value.replace(/\D/g, '').slice(0, 2)
  if (val.length === 2) {
    const n = parseInt(val)
    if (n > 12) val = '12'; else if (n < 1) val = '01'
  }
  monthVal.value = val; el.value = val
  if (val.length === 2 || (val.length === 1 && parseInt(val) > 1)) {
    if (val.length === 1) { monthVal.value = `0${val}`; el.value = monthVal.value }
    dayRef.value?.focus()
  }
}

function onDayInput(e: Event) {
  const el = e.target as HTMLInputElement
  let val = el.value.replace(/\D/g, '').slice(0, 2)
  if (val.length === 2) {
    const n = parseInt(val)
    if (n > 31) val = '31'; else if (n < 1) val = '01'
  }
  dayVal.value = val; el.value = val
  if (val.length === 1 && parseInt(val) > 3) { dayVal.value = `0${val}`; el.value = dayVal.value }
}

function onMonthKeydown(e: KeyboardEvent) {
  if (e.key === 'Backspace' && monthVal.value === '') {
    e.preventDefault(); yearRef.value?.focus()
    yearVal.value = yearVal.value.slice(0, -1)
    if (yearRef.value) yearRef.value.value = yearVal.value
  }
}

function onDayKeydown(e: KeyboardEvent) {
  if (e.key === 'Backspace' && dayVal.value === '') {
    e.preventDefault(); monthRef.value?.focus()
    monthVal.value = monthVal.value.slice(0, -1)
    if (monthRef.value) monthRef.value.value = monthVal.value
  }
}

// ── 시각 분리 입력 ──────────────────────────────────────────────────
const hourRef   = ref<HTMLInputElement | null>(null)
const minuteRef = ref<HTMLInputElement | null>(null)
const hourVal   = ref('12')
const minuteVal = ref('00')

watch([hourVal, minuteVal], () => {
  const h = hourVal.value.padStart(2, '0')
  const m = minuteVal.value.padStart(2, '0')
  if (hourVal.value !== '' && minuteVal.value !== '') form.birth_time = `${h}:${m}`
})

function onHourInput(e: Event) {
  const el = e.target as HTMLInputElement
  let val = el.value.replace(/\D/g, '').slice(0, 2)
  if (val.length === 2) {
    const n = parseInt(val)
    if (n > 23) val = '23'
  }
  hourVal.value = val; el.value = val
  if (val.length === 2 || (val.length === 1 && parseInt(val) > 2)) {
    if (val.length === 1) { hourVal.value = `0${val}`; el.value = hourVal.value }
    minuteRef.value?.focus()
  }
}

function onMinuteInput(e: Event) {
  const el = e.target as HTMLInputElement
  let val = el.value.replace(/\D/g, '').slice(0, 2)
  if (val.length === 2) {
    const n = parseInt(val)
    if (n > 59) val = '59'
  }
  minuteVal.value = val; el.value = val
}

function onMinuteKeydown(e: KeyboardEvent) {
  if (e.key === 'Backspace' && minuteVal.value === '') {
    e.preventDefault(); hourRef.value?.focus()
    hourVal.value = hourVal.value.slice(0, -1)
    if (hourRef.value) hourRef.value.value = hourVal.value
  }
}

// ── 도시 검색 ────────────────────────────────────────────────────────
const cityQuery    = ref('')
const cityResults  = ref<CityOption[]>([])
const selectedCity = ref<CityOption | null>(null)
const cityOpen     = ref(false)
const cityInputRef = ref<HTMLInputElement | null>(null)
const cityLoading  = ref(false)

const correction = computed(() => {
  const city = selectedCity.value
  if (!city) return SEOUL_CORRECTION
  return calcSolarCorrection(city.longitude, city.utcOffset)
})

let _debounceTimer: ReturnType<typeof setTimeout> | null = null

// 시시(時辰) 목록 — 시작 분(0~1439) 기준
const SISI: { name: string; start: number; end: number; range: string }[] = [
  { name: '자시', start: 23*60+30, end: 25*60+30, range: '23:30~01:30' },
  { name: '축시', start:  1*60+30, end:  3*60+30, range: '01:30~03:30' },
  { name: '인시', start:  3*60+30, end:  5*60+30, range: '03:30~05:30' },
  { name: '묘시', start:  5*60+30, end:  7*60+30, range: '05:30~07:30' },
  { name: '진시', start:  7*60+30, end:  9*60+30, range: '07:30~09:30' },
  { name: '사시', start:  9*60+30, end: 11*60+30, range: '09:30~11:30' },
  { name: '오시', start: 11*60+30, end: 13*60+30, range: '11:30~13:30' },
  { name: '미시', start: 13*60+30, end: 15*60+30, range: '13:30~15:30' },
  { name: '신시', start: 15*60+30, end: 17*60+30, range: '15:30~17:30' },
  { name: '유시', start: 17*60+30, end: 19*60+30, range: '17:30~19:30' },
  { name: '술시', start: 19*60+30, end: 21*60+30, range: '19:30~21:30' },
  { name: '해시', start: 21*60+30, end: 23*60+30, range: '21:30~23:30' },
]

function getSisi(totalMin: number) {
  const t = ((totalMin % 1440) + 1440) % 1440
  if (t >= 23*60+30 || t < 1*60+30) return SISI[0]
  return SISI.find(s => t >= s.start && t < s.end) ?? null
}

function fmtMinutes(min: number) {
  const t = ((min % 1440) + 1440) % 1440
  const h = String(Math.floor(t / 60)).padStart(2, '0')
  const m = String(t % 60).padStart(2, '0')
  return `${h}:${m}`
}

// 보정 적용 후 시각 + 시시 미리보기
const correctedPreview = computed(() => {
  const h = parseInt(hourVal.value || '0')
  const m = parseInt(minuteVal.value || '0')
  if (isNaN(h) || isNaN(m)) return null
  const inputMin  = h * 60 + m
  const corrMin   = correction.value
  const appliedMin = inputMin + corrMin
  const sisi = getSisi(appliedMin)
  return {
    correction: corrMin,
    applied: fmtMinutes(appliedMin),
    sisi,
  }
})

function onCityInput(e: Event) {
  const q = (e.target as HTMLInputElement).value
  cityQuery.value = q
  selectedCity.value = null
  if (!q.trim()) { cityResults.value = []; cityOpen.value = false; return }
  if (_debounceTimer) clearTimeout(_debounceTimer)
  cityLoading.value = true
  _debounceTimer = setTimeout(async () => {
    cityResults.value = await searchCities(q)
    cityLoading.value = false
    cityOpen.value = cityResults.value.length > 0
  }, 300)
}

function selectCity(city: CityOption) {
  selectedCity.value = city
  cityQuery.value = city.label
  cityResults.value = []
  cityOpen.value = false
}

function clearCity() {
  selectedCity.value = null
  cityQuery.value = ''
  cityResults.value = []
  cityOpen.value = false
  nextTick(() => cityInputRef.value?.focus())
}

function onCityBlur() {
  setTimeout(() => { cityOpen.value = false }, 150)
}

// ── 제출 ─────────────────────────────────────────────────────────────
function onSubmit() {
  if (!form.birth_date) return
  const req: SajuCalcRequest = { ...form }
  if (selectedCity.value) {
    req.birth_longitude = selectedCity.value.longitude
    if (!selectedCity.value.isKorea) req.birth_utc_offset = selectedCity.value.utcOffset
  }
  emit('submit', req)
}
</script>

<template>
  <form
    class="relative w-full space-y-7 rounded-2xl px-8 pt-5 pb-6"
    style="background: #ffffff; border: 1px solid #e8e2db;"
    @submit.prevent="onSubmit"
  >
    <div
      class="pointer-events-none absolute -right-3 -top-4 font-serif text-[7rem] leading-none font-bold select-none"
      style="color: rgba(166,124,82,0.04); letter-spacing: 0.05em; overflow: hidden; max-width: 60%;"
      aria-hidden="true"
    >四柱</div>

    <div class="relative space-y-4">

      <!-- 이름 -->
      <div class="space-y-1">
        <label class="text-xs tracking-wider uppercase" style="color: #aaaaaa;">이름</label>
        <input v-model="form.name" type="text" placeholder="홍길동"
          class="input-underline" style="font-size: 18px;" />
      </div>

      <!-- 출생지 -->
      <div class="space-y-1">
        <label class="text-xs tracking-wider uppercase" style="color: #aaaaaa;">출생지</label>
        <div class="relative">
          <div class="flex items-center gap-2" style="border-bottom: 1px solid #ddd7d0;">
            <svg class="w-4 h-4 flex-shrink-0" style="color: #bbbbbb;" fill="none"
              stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
            <input ref="cityInputRef" type="text" :value="cityQuery"
              placeholder="도시명 검색 (예: 서울, 도쿄, 뉴욕)"
              class="city-input" style="font-size: 15px; padding: 6px 0;"
              autocomplete="off"
              @input="onCityInput"
              @focus="cityOpen = cityResults.length > 0"
              @blur="onCityBlur" />
            <button v-if="selectedCity" type="button"
              class="flex-shrink-0 text-sm" style="color: #bbbbbb;"
              @click="clearCity">✕</button>
          </div>
          <ul v-if="cityLoading" class="city-dropdown">
            <li class="city-item" style="color: #aaaaaa;">검색 중...</li>
          </ul>
          <ul v-else-if="cityOpen && cityResults.length" class="city-dropdown">
            <li v-for="city in cityResults" :key="city.label + city.timezone"
              class="city-item" @mousedown.prevent="selectCity(city)">
              <span class="city-item-label">{{ city.label }}</span>
              <span class="city-item-sub">{{ city.sublabel }}</span>
            </li>
          </ul>
        </div>
        <p class="text-xs" style="color: #aaaaaa;">
          {{ selectedCity ? selectedCity.timezone : '미입력 시 서울 기준 적용' }}
        </p>
      </div>

      <!-- 생년월일 + 시각 (한 줄) -->
      <div class="space-y-1">
        <label class="text-xs tracking-wider uppercase" style="color: #aaaaaa;">생년월일 · 시각</label>
        <!-- 날짜 + 시각 + 토글 -->
        <div class="flex items-center gap-3">
          <!-- 날짜 + 시각 입력 -->
          <div class="flex-1 min-w-0 flex items-baseline" style="border-bottom: 1px solid #ddd7d0;">
            <input ref="yearRef" type="text" inputmode="numeric" placeholder="YYYY" maxlength="4"
              class="date-seg" style="flex: 2; min-width: 0;" @input="onYearInput" />
            <span class="date-sep" style="padding: 0 1px;">/</span>
            <input ref="monthRef" type="text" inputmode="numeric" placeholder="MM" maxlength="2"
              class="date-seg" style="flex: 1; min-width: 0;"
              @input="onMonthInput" @keydown="onMonthKeydown" />
            <span class="date-sep" style="padding: 0 1px;">/</span>
            <input ref="dayRef" type="text" inputmode="numeric" placeholder="DD" maxlength="2"
              class="date-seg" style="flex: 1; min-width: 0;"
              @input="onDayInput" @keydown="onDayKeydown" />
            <span class="date-sep" style="padding: 0 4px; color: #d0cac4;">·</span>
            <input ref="hourRef" type="text" inputmode="numeric" placeholder="HH" maxlength="2"
              :value="hourVal" class="date-seg" style="flex: 1; min-width: 0;"
              @input="onHourInput" />
            <span class="date-sep" style="padding: 0 1px;">:</span>
            <input ref="minuteRef" type="text" inputmode="numeric" placeholder="MM" maxlength="2"
              :value="minuteVal" class="date-seg" style="flex: 1; min-width: 0;"
              @input="onMinuteInput" @keydown="onMinuteKeydown" />
          </div>
          <!-- 양력/음력/윤달 토글 -->
          <div class="flex gap-1 p-0.5 rounded-full shrink-0" style="background: #f0ece8;">
            <button type="button" class="pill-toggle !text-xs !px-3 !py-1"
              :class="form.calendar === 'solar' ? 'pill-toggle-active' : 'pill-toggle-inactive'"
              @click="form.calendar = 'solar'; form.is_leap_month = false">양력</button>
            <button type="button" class="pill-toggle !text-xs !px-3 !py-1"
              :class="form.calendar === 'lunar' && !form.is_leap_month ? 'pill-toggle-active' : 'pill-toggle-inactive'"
              @click="form.calendar = 'lunar'; form.is_leap_month = false">음력</button>
            <button type="button" class="pill-toggle !text-xs !px-3 !py-1 transition-opacity"
              :class="form.calendar === 'lunar' && form.is_leap_month ? 'pill-toggle-active' : 'pill-toggle-inactive'"
              :style="form.calendar !== 'lunar' ? 'opacity: 0.35; cursor: default;' : ''"
              :disabled="form.calendar !== 'lunar'"
              @click="form.is_leap_month = !form.is_leap_month">윤달</button>
          </div>
        </div>
        <!-- 보정 미리보기 -->
        <div v-if="correctedPreview && (hourVal || minuteVal)"
          class="flex items-center gap-1.5 text-xs flex-wrap" style="color: #888888;">
          <span>{{ formatCorrection(correctedPreview.correction) }} 보정</span>
          <span style="color: #cccccc;">→</span>
          <span style="color: #555555; font-variant-numeric: tabular-nums;">{{ correctedPreview.applied }}</span>
          <span v-if="correctedPreview.sisi"
            class="px-1.5 py-0.5 rounded font-medium"
            style="background: #f5f0eb; color: #7a6650;">
            {{ correctedPreview.sisi.name }}
          </span>
          <span v-if="correctedPreview.sisi" style="color: #bbbbbb;">{{ correctedPreview.sisi.range }}</span>
        </div>
      </div>

      <!-- 성별 -->
      <div class="space-y-1">
        <label class="text-xs tracking-wider uppercase" style="color: #aaaaaa;">성별</label>
        <div class="flex gap-2 p-1 rounded-full w-full" style="background: #f0ece8;">
          <button type="button" class="pill-toggle flex-1"
            :class="form.gender === 'male' ? 'pill-toggle-active' : 'pill-toggle-inactive'"
            @click="form.gender = 'male'">남성</button>
          <button type="button" class="pill-toggle flex-1"
            :class="form.gender === 'female' ? 'pill-toggle-active' : 'pill-toggle-inactive'"
            @click="form.gender = 'female'">여성</button>
        </div>
      </div>

      <button type="submit" class="btn-primary w-full mt-1 text-base">
        사주 계산하기
      </button>
    </div>
  </form>
</template>
