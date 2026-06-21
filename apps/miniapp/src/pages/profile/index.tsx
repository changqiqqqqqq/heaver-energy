import { Text, View } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useEffect, useState } from 'react'

import AppButton from '@/components/AppButton'
import { authApi } from '@/services/auth.api'
import { getLatestSubmission } from '@/store/questionnaire.store'
import { clearSession, getCachedUser, type AppUser } from '@/store/user.store'

import './index.css'

export default function ProfilePage() {
  const [user, setUser] = useState<AppUser | undefined>(() => getCachedUser())
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const cachedUser = getCachedUser()
    if (cachedUser) {
      setUser(cachedUser)
    }
  }, [])

  const login = async () => {
    try {
      setLoading(true)
      const loginUser = await authApi.ensureLogin()
      setUser(loginUser)
      authApi.getMe().then(setUser).catch(() => undefined)
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    clearSession()
    setUser(undefined)
    Taro.showToast({ title: '已退出登录', icon: 'none' })
  }

  const goLatestResult = () => {
    const submission = getLatestSubmission()
    if (!submission) {
      Taro.showToast({ title: '暂无测评结果', icon: 'none' })
      return
    }
    Taro.navigateTo({ url: `/pages/questionnaire-result/index?submissionId=${submission.id}` })
  }

  return (
    <View className="profile-page">
      <View className="profile-card">
        <View className="profile-avatar">
          <Text className="profile-avatar-text">⌁</Text>
        </View>
        <View className="profile-main">
          <Text className="profile-name">{user?.nickname || '河狸能源用户'}</Text>
          <Text className="profile-meta">{user?.phone_masked || (user ? '手机号未授权' : '登录后同步测评和服务进度')}</Text>
        </View>
      </View>

      <View className="profile-actions">
        {user ? (
          <AppButton text="刷新账号信息" variant="light" loading={loading} disabled={loading} onClick={login} />
        ) : (
          <AppButton text="微信登录" loading={loading} disabled={loading} onClick={login} />
        )}
      </View>

      <View className="profile-menu">
        <View className="profile-menu-item" onClick={goLatestResult}>
          <View>
            <Text className="menu-title">我的测评结果</Text>
            <Text className="menu-desc">查看最近一次经营体质画像</Text>
          </View>
          <Text className="menu-arrow">›</Text>
        </View>
        <View className="profile-menu-item" onClick={() => Taro.navigateTo({ url: '/pages/screening/index' })}>
          <View>
            <Text className="menu-title">免费商电优化报告</Text>
            <Text className="menu-desc">提交企业信息领取初筛建议</Text>
          </View>
          <Text className="menu-arrow">›</Text>
        </View>
        <View className="profile-menu-item" onClick={() => Taro.navigateTo({ url: '/pages/service-request/index' })}>
          <View>
            <Text className="menu-title">顾问咨询</Text>
            <Text className="menu-desc">提交用能、报价或供应商问题</Text>
          </View>
          <Text className="menu-arrow">›</Text>
        </View>
      </View>

      {user ? (
        <View className="profile-logout" onClick={logout}>
          <Text className="profile-logout-text">退出登录</Text>
        </View>
      ) : null}
    </View>
  )
}

