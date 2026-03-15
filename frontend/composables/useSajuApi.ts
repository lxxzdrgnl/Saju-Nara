import type { SajuCalcRequest, SajuCalcResponse, WolUnEntry, YeonUnEntry, IlJinEntry, DailyFortuneRequest, DailyFortuneResponse } from '~/types/saju'

export function useSajuApi() {
  const config = useRuntimeConfig()
  const base = config.public.apiBase

  async function calcSaju(req: SajuCalcRequest): Promise<SajuCalcResponse> {
    const data = await $fetch<SajuCalcResponse>(`${base}/api/saju/calc`, {
      method: 'POST',
      body: req,
    })
    return data
  }

  async function getWolUn(year: number, dayStem: string): Promise<WolUnEntry[]> {
    return $fetch<WolUnEntry[]>(`${base}/api/saju/wol-un`, {
      query: { year, day_stem: dayStem },
    })
  }

  async function getYeonUn(startYear: number, count: number, dayStem: string): Promise<YeonUnEntry[]> {
    return $fetch<YeonUnEntry[]>(`${base}/api/saju/yeon-un`, {
      query: { start_year: startYear, count, day_stem: dayStem },
    })
  }

  async function getIlJin(year: number, month: number): Promise<IlJinEntry[]> {
    return $fetch<IlJinEntry[]>(`${base}/api/saju/il-jin`, {
      query: { year, month },
    })
  }

  async function getDailyFortune(req: DailyFortuneRequest): Promise<DailyFortuneResponse> {
    return $fetch<DailyFortuneResponse>(`${base}/api/saju/daily`, {
      method: 'POST',
      body: req,
    })
  }

  async function createDailyShare(birthInput: Record<string, unknown>): Promise<{ share_token: string; share_url: string }> {
    return $fetch(`${base}/api/share/daily`, {
      method: 'POST',
      body: { birth_input: birthInput },
    })
  }

  async function getDailyShareInput(token: string): Promise<{ birth_input: Record<string, unknown> }> {
    return $fetch(`${base}/api/share/daily/${token}`)
  }

  return { calcSaju, getWolUn, getYeonUn, getIlJin, getDailyFortune, createDailyShare, getDailyShareInput }
}
