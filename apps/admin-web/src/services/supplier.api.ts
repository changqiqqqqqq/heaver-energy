import { ADMIN_API_PREFIX, request } from './http'

export type Supplier = {
  id: number
  name: string
  supplier_type: string
  region_scope_json?: string[] | null
  service_tags_json?: string[] | null
  contact_name?: string | null
  contact_phone_masked?: string | null
  status: string
  remark?: string | null
}

export type SupplierCreatePayload = {
  name: string
  supplier_type: string
  region_scope: string[]
  service_tags: string[]
  contact_name?: string
  contact_phone_masked?: string
  remark?: string
}

export const supplierApi = {
  list() {
    return request<Supplier[]>(`${ADMIN_API_PREFIX}/suppliers`)
  },

  create(payload: SupplierCreatePayload) {
    return request<Supplier>(`${ADMIN_API_PREFIX}/suppliers`, {
      method: 'POST',
      data: payload,
    })
  },

  transfer(payload: { lead_id: number; supplier_id: number; service_request_id?: number; transfer_reason?: string }) {
    return request(`${ADMIN_API_PREFIX}/suppliers/transfers`, {
      method: 'POST',
      data: payload,
    })
  },
}

