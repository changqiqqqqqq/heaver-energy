import { APP_API_PREFIX, request } from '@/services/http'

export type FileMetadataPayload = {
  biz_type: string
  biz_id?: number | null
  object_key: string
  original_filename?: string
  mime_type?: string
  file_size?: number
  sha256?: string
  sensitivity_level?: string
  access_policy?: string
}

export const fileApi = {
  createFile(payload: FileMetadataPayload) {
    return request<{ id: number }>({
      url: `${APP_API_PREFIX}/files`,
      method: 'POST',
      data: payload,
    })
  },

  createBillUpload(payload: { lead_id?: number | null; enterprise_id?: number | null; file_id: number; bill_month?: string }) {
    return request({
      url: `${APP_API_PREFIX}/bills`,
      method: 'POST',
      data: payload,
    })
  },
}
