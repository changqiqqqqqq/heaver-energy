import Taro from '@tarojs/taro'

import { clearSession, getAccessToken } from '@/store/user.store'

export const API_BASE_URL = 'http://101.34.67.122'
export const APP_API_PREFIX = '/api/app'

export type ApiResponse<T> = {
  code: number
  message: string
  data: T | null
}

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE'

type RequestOptions<TBody> = {
  url: string
  method?: HttpMethod
  data?: TBody
  auth?: boolean
  showError?: boolean
}

const normalizeUrl = (url: string) => {
  if (url.startsWith('http')) {
    return url
  }
  return `${API_BASE_URL}${url}`
}

const getErrorMessage = (error: unknown) => {
  if (error instanceof Error) {
    return error.message
  }

  const errMsg = (error as { errMsg?: string })?.errMsg
  return errMsg || '网络异常，请稍后重试'
}

export class RequestError extends Error {
  statusCode?: number

  constructor(message: string, statusCode?: number) {
    super(message)
    this.statusCode = statusCode
  }
}

export async function request<TData, TBody = unknown>(options: RequestOptions<TBody>): Promise<TData> {
  const token = getAccessToken()
  const needAuth = options.auth !== false

  const header: Record<string, string> = {
    'content-type': 'application/json',
  }

  if (needAuth && token) {
    header.Authorization = `Bearer ${token}`
  }

  try {
    const response = await Taro.request<ApiResponse<TData>>({
      url: normalizeUrl(options.url),
      method: options.method || 'GET',
      data: options.data,
      header,
    })

    if (response.statusCode === 401) {
      clearSession()
      throw new RequestError('登录已失效，请重新登录', response.statusCode)
    }

    if (response.statusCode < 200 || response.statusCode >= 300) {
      const detail = (response.data as unknown as { detail?: string })?.detail
      throw new RequestError(detail || `请求失败：${response.statusCode}`, response.statusCode)
    }

    const body = response.data
    if (body.code !== 0) {
      throw new RequestError(body.message || '请求失败', response.statusCode)
    }

    return body.data as TData
  } catch (error) {
    const message = getErrorMessage(error)
    if (options.showError !== false) {
      Taro.showToast({ title: message, icon: 'none' })
    }
    throw error
  }
}
