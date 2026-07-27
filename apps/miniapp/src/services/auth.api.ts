import Taro from '@tarojs/taro'

import { APP_API_PREFIX, request } from '@/services/http'
import { getAccessToken, getCachedUser, setSession, updateCachedUser, type AppUser } from '@/store/user.store'

export type AuthTokenResponse = {
  access_token: string
  token_type: string
  expires_in: number
  user: AppUser
}

export type PhoneAuthorizeResponse = {
  user: AppUser
  phone_authorized: boolean
}

type LoginOptions = {
  showError?: boolean
}

export const authApi = {
  async loginWithWechat(options: LoginOptions = {}): Promise<AuthTokenResponse> {
    const loginResult = await Taro.login()
    if (!loginResult.code) {
      throw new Error('微信登录失败，请重试')
    }

    const token = await request<AuthTokenResponse>({
      url: `${APP_API_PREFIX}/auth/wechat-login`,
      method: 'POST',
      auth: false,
      showError: options.showError,
      data: {
        code: loginResult.code,
      },
    })

    setSession(token.access_token, token.user)
    return token
  },

  async ensureLogin(options: LoginOptions = {}): Promise<AppUser> {
    const cachedUser = getCachedUser()
    if (getAccessToken() && cachedUser) {
      return cachedUser
    }

    const token = await this.loginWithWechat(options)
    return token.user
  },

  async getMe(): Promise<AppUser> {
    const user = await request<AppUser>({
      url: `${APP_API_PREFIX}/auth/me`,
    })
    updateCachedUser(user)
    return user
  },

  async authorizePhone(payload: { phone_code?: string; dev_phone_number?: string }): Promise<PhoneAuthorizeResponse> {
    await this.ensureLogin()

    const response = await request<PhoneAuthorizeResponse>({
      url: `${APP_API_PREFIX}/auth/phone-authorize`,
      method: 'POST',
      data: {
        ...payload,
        consent_version: 'v1',
        granted: true,
      },
    })

    updateCachedUser(response.user)
    return response
  },
}
