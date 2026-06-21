export type AuthState = {
  token?: string
  admin?: AdminUser
}

export type AdminUser = {
  id: number
  username: string
  display_name: string
  phone_masked?: string | null
  status: string
}

export const initialAuthState: AuthState = {}

const TOKEN_KEY = 'heaver.admin.token'
const ADMIN_KEY = 'heaver.admin.user'

export function getAdminToken(): string {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function getCachedAdmin(): AdminUser | undefined {
  const raw = localStorage.getItem(ADMIN_KEY)
  if (!raw) {
    return undefined
  }
  try {
    return JSON.parse(raw) as AdminUser
  } catch {
    return undefined
  }
}

export function setAdminSession(token: string, admin: AdminUser): void {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(ADMIN_KEY, JSON.stringify(admin))
}

export function updateCachedAdmin(admin: AdminUser): void {
  localStorage.setItem(ADMIN_KEY, JSON.stringify(admin))
}

export function clearAdminSession(): void {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(ADMIN_KEY)
}

export function hasAdminToken(): boolean {
  return Boolean(getAdminToken())
}

