import { clearAdminSession, getAdminToken } from '../store/auth.store'

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'https://api.helicloud.cn').replace(/\/$/, '')
export const ADMIN_API_PREFIX = '/api/admin'

export type ApiResponse<T> = {
  code: number
  message: string
  data: T | null
}

type RequestOptions = {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: unknown
  auth?: boolean
}

export class RequestError extends Error {
  statusCode?: number

  constructor(message: string, statusCode?: number) {
    super(message)
    this.statusCode = statusCode
  }
}

function normalizeUrl(url: string): string {
  return url.startsWith('http') ? url : `${API_BASE_URL}${url}`
}

export function withQuery(url: string, query: Record<string, unknown>): string {
  const params = new URLSearchParams()
  Object.entries(query).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.set(key, String(value))
    }
  })
  const queryString = params.toString()
  return queryString ? `${url}?${queryString}` : url
}

export async function request<T>(url: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {
    'content-type': 'application/json',
  }
  const needAuth = options.auth !== false
  const token = getAdminToken()
  if (needAuth && token) {
    headers.Authorization = `Bearer ${token}`
  }

  const response = await fetch(normalizeUrl(url), {
    method: options.method || 'GET',
    headers,
    body: options.data === undefined ? undefined : JSON.stringify(options.data),
  })

  if (response.status === 401) {
    clearAdminSession()
    if (!window.location.pathname.includes('/login')) {
      window.location.href = '/login'
    }
    throw new RequestError('登录已失效，请重新登录', response.status)
  }

  const body = (await response.json().catch(() => null)) as ApiResponse<T> | { detail?: string } | null
  if (!response.ok) {
    const detail = body && 'detail' in body ? body.detail : ''
    throw new RequestError(detail || `请求失败：${response.status}`, response.status)
  }

  if (!body || !('code' in body)) {
    throw new RequestError('接口响应格式不正确', response.status)
  }
  if (body.code !== 0) {
    throw new RequestError(body.message || '请求失败', response.status)
  }

  return body.data as T
}
