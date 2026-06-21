import Taro from '@tarojs/taro'

export type AppUser = {
  id: number
  nickname?: string | null
  avatar_url?: string | null
  phone_masked?: string | null
  status: string
  has_phone_authorized: boolean
}

export type UserState = {
  accessToken?: string
  expiresIn?: number
  user?: AppUser
}

export const initialUserState: UserState = {}

const TOKEN_KEY = 'heaver.access_token'
const USER_KEY = 'heaver.user'

export const getAccessToken = () => {
  return Taro.getStorageSync<string>(TOKEN_KEY) || ''
}

export const getCachedUser = (): AppUser | undefined => {
  return Taro.getStorageSync<AppUser>(USER_KEY) || undefined
}

export const setSession = (accessToken: string, user: AppUser) => {
  Taro.setStorageSync(TOKEN_KEY, accessToken)
  Taro.setStorageSync(USER_KEY, user)
}

export const updateCachedUser = (user: AppUser) => {
  Taro.setStorageSync(USER_KEY, user)
}

export const clearSession = () => {
  Taro.removeStorageSync(TOKEN_KEY)
  Taro.removeStorageSync(USER_KEY)
}

export const hasLogin = () => {
  return Boolean(getAccessToken())
}
