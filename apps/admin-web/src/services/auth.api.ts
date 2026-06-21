import { updateCachedAdmin, setAdminSession, type AdminUser } from '../store/auth.store'
import { ADMIN_API_PREFIX, request } from './http'

export type AdminLoginResponse = {
  access_token: string
  token_type: string
  expires_in: number
  admin: AdminUser
}

export const authApi = {
  async login(username: string, password: string): Promise<AdminLoginResponse> {
    const data = await request<AdminLoginResponse>(`${ADMIN_API_PREFIX}/auth/login`, {
      method: 'POST',
      auth: false,
      data: { username, password },
    })
    setAdminSession(data.access_token, data.admin)
    return data
  },

  async me(): Promise<AdminUser> {
    const admin = await request<AdminUser>(`${ADMIN_API_PREFIX}/auth/me`)
    updateCachedAdmin(admin)
    return admin
  },

  async logout(): Promise<void> {
    await request(`${ADMIN_API_PREFIX}/auth/logout`, { method: 'POST' })
  },
}

