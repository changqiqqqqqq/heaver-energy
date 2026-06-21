import { APP_API_PREFIX, request } from '@/services/http'

export type ScreeningPayload = {
  lead_id?: number | null
  submission_id?: number | null
  enterprise_id?: number | null
  region_text?: string
  enterprise_name?: string
  enterprise_type?: string
  monthly_kwh_range?: string
  contact_name?: string
  contact_phone?: string
  extra?: Record<string, unknown>
}

export type ScreeningResponse = {
  id: number
  user_id: number
  enterprise_id?: number | null
  lead_id?: number | null
  region_text?: string | null
  enterprise_name?: string | null
  enterprise_type?: string | null
  monthly_kwh_range?: string | null
  contact_name?: string | null
  contact_phone_masked?: string | null
  bill_upload_status: string
  status: string
  submitted_at: string
}

export const screeningApi = {
  submit(payload: ScreeningPayload) {
    return request<ScreeningResponse, ScreeningPayload>({
      url: `${APP_API_PREFIX}/screening-requests`,
      method: 'POST',
      data: payload,
    })
  },
}
