import { ADMIN_API_PREFIX, request, withQuery } from './http'

export type PageResult<T> = {
  items: T[]
  total: number
  page: number
  page_size: number
}

export type LeadListItem = {
  id: number
  lead_no: string
  enterprise_id?: number | null
  enterprise_name?: string | null
  source_entry?: string | null
  lead_grade?: string | null
  lead_status: string
  primary_need_type?: string | null
  profile_code?: string | null
  result_summary?: string | null
  has_bill_uploaded: boolean
  has_phone_authorized: boolean
  last_activity_at?: string | null
  created_at: string
}

export type LeadDetail = {
  id: number
  lead_no: string
  enterprise_id?: number | null
  enterprise_name?: string | null
  user_id?: number | null
  source_channel: string
  source_entry?: string | null
  lead_grade?: string | null
  lead_status: string
  primary_need_type?: string | null
  profile_code?: string | null
  result_summary?: string | null
  has_bill_uploaded: boolean
  has_phone_authorized: boolean
  score_snapshot?: Record<string, unknown> | null
  need_tags: string[]
  assigned_admin_id?: number | null
  first_submitted_at?: string | null
  last_activity_at?: string | null
  submissions: Array<Record<string, unknown>>
  screenings: Array<Record<string, unknown>>
  service_requests: Array<Record<string, unknown>>
  bill_uploads: Array<Record<string, unknown>>
  followups: Array<Record<string, unknown>>
  notes: Array<Record<string, unknown>>
  transfers: Array<Record<string, unknown>>
}

export type LeadSensitive = {
  lead_id: number
  phone_masked?: string | null
  phone_cipher?: string | null
  contact_name?: string | null
}

export type LeadQuery = {
  page?: number
  page_size?: number
  lead_grade?: string
  lead_status?: string
  profile_code?: string
  primary_need_type?: string
  has_bill_uploaded?: boolean | ''
  has_phone_authorized?: boolean | ''
}

export type FollowupPayload = {
  lead_id: number
  followup_type: string
  followup_result: string
  content?: string
  next_followup_at?: string
}

export const leadApi = {
  list(query: LeadQuery) {
    return request<PageResult<LeadListItem>>(withQuery(`${ADMIN_API_PREFIX}/leads`, query))
  },

  detail(id: number) {
    return request<LeadDetail>(`${ADMIN_API_PREFIX}/leads/${id}`)
  },

  updateStatus(id: number, lead_status: string, remark?: string) {
    return request(`${ADMIN_API_PREFIX}/leads/${id}/status`, {
      method: 'POST',
      data: { lead_status, remark },
    })
  },

  sensitive(id: number) {
    return request<LeadSensitive>(`${ADMIN_API_PREFIX}/leads/${id}/sensitive`)
  },

  createFollowup(payload: FollowupPayload) {
    return request(`${ADMIN_API_PREFIX}/crm/followups`, {
      method: 'POST',
      data: payload,
    })
  },

  createNote(lead_id: number, content: string, note_type = 'general') {
    return request(`${ADMIN_API_PREFIX}/crm/notes`, {
      method: 'POST',
      data: { lead_id, content, note_type },
    })
  },
}

