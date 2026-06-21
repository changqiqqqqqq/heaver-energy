import { ADMIN_API_PREFIX, request, withQuery } from './http'

export type DashboardMetricCard = {
  key: 'visits' | 'submissions' | 'reports' | 'consultations' | string
  label: string
  value: number
  change_rate: number
}

export type DashboardTrendItem = {
  date: string
  visits: number
  submissions: number
  reports: number
  consultations: number
}

export type DashboardFunnelStep = {
  key: string
  label: string
  value: number
  conversion_rate: number
}

export type DashboardProfileDistributionItem = {
  profile_code: string
  profile_name: string
  count: number
  ratio: number
  consultation_rate: number
}

export type DashboardPendingMessageItem = {
  lead_id: number
  lead_no: string
  display_name: string
  profile_code?: string | null
  profile_name?: string | null
  content: string
  status: string
  minutes_ago?: number | null
}

export type DashboardOverview = {
  date: string
  cards: DashboardMetricCard[]
  trend: DashboardTrendItem[]
  funnel: DashboardFunnelStep[]
  profile_distribution: DashboardProfileDistributionItem[]
  pending_messages: DashboardPendingMessageItem[]
}

export const statisticsApi = {
  getOverview(date?: string) {
    return request<DashboardOverview>(withQuery(`${ADMIN_API_PREFIX}/dashboard/overview`, { date }))
  },
}

