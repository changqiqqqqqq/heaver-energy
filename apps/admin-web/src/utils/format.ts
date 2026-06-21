export function formatEmpty(value: unknown): string {
  return value === undefined || value === null || value === '' ? '-' : String(value)
}

export function formatNumber(value: number | undefined | null): string {
  return new Intl.NumberFormat('zh-CN').format(value || 0)
}

export function formatPercent(value: number | undefined | null): string {
  return `${(value || 0).toFixed(1)}%`
}

export function formatDateTime(value: string | undefined | null): string {
  if (!value) {
    return '-'
  }
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

export const PROFILE_LABELS: Record<string, string> = {
  hidden_waste: '隐性浪费型',
  energy_awakened: '能源觉醒型',
  supplier_confused: '供应商迷茫型',
  cost_sensitive: '成本敏感型',
  growth_expansion: '增长扩张型',
  stable_operation: '稳健经营型',
}

export const LEAD_STATUS_LABELS: Record<string, string> = {
  pending_followup: '待跟进',
  following: '跟进中',
  transferred_supplier: '已转接',
  content_saved: '已留存',
  closed: '已关闭',
}

export const NEED_TYPE_LABELS: Record<string, string> = {
  use_energy: '用能咨询',
  energy_consulting: '商电成本核查',
  supplier_recommendation: '供应商推荐',
  quote_review: '报价方案判断',
  supplier_screening: '供应商筛选',
  contract_review: '合同审查',
  green_power: '绿电',
  green_certificate: '绿证',
  solar_storage: '光储方案',
}

