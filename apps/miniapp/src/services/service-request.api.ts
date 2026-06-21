import { APP_API_PREFIX, request } from '@/services/http'

export type NeedType =
  | 'use_energy'
  | 'energy_consulting'
  | 'supplier_recommendation'
  | 'quote_review'
  | 'supplier_screening'
  | 'contract_review'
  | 'green_power'
  | 'green_certificate'
  | 'solar_storage'

export type ServiceRequestPayload = {
  lead_id?: number | null
  enterprise_id?: number | null
  submission_id?: number | null
  primary_need_type?: NeedType
  description?: string
  items: Array<{
    need_type: NeedType
    need_name: string
    extra?: Record<string, unknown>
  }>
}

export type ServiceRequestItemResponse = {
  id: number
  service_request_id: number
  need_type: string
  need_name: string
  extra_json?: Record<string, unknown> | null
}

export type ServiceRequestResponse = {
  id: number
  request_no: string
  user_id: number
  enterprise_id?: number | null
  lead_id?: number | null
  submission_id?: number | null
  primary_need_type?: string | null
  description?: string | null
  status: string
  submitted_at: string
  items: ServiceRequestItemResponse[]
}

export const serviceRequestApi = {
  submit(payload: ServiceRequestPayload) {
    return request<ServiceRequestResponse, ServiceRequestPayload>({
      url: `${APP_API_PREFIX}/service-requests`,
      method: 'POST',
      data: payload,
    })
  },
}
