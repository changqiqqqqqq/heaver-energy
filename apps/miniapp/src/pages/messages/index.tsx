import { Text, View } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useEffect, useMemo, useState } from 'react'

import AppButton from '@/components/AppButton'
import { authApi } from '@/services/auth.api'
import { getAccessToken, getCachedUser, type AppUser } from '@/store/user.store'

import './index.css'

type MessageType = 'notice' | 'progress'

type MessageItem = {
  id: string
  type: MessageType
  icon: string
  title: string
  time: string
  desc: string
  unread?: boolean
  url: string
}

const tabs: Array<{ label: string; type: 'all' | MessageType }> = [
  { label: '全部', type: 'all' },
  { label: '通知', type: 'notice' },
  { label: '服务进度', type: 'progress' },
]

const messages: MessageItem[] = []

export default function MessagesPage() {
  const [user, setUser] = useState<AppUser | undefined>(() => getCachedUser())
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'all' | MessageType>('all')

  useEffect(() => {
    if (!getAccessToken()) {
      return
    }
    authApi.getMe().then(setUser).catch(() => {})
  }, [])

  const filteredMessages = useMemo(() => {
    if (activeTab === 'all') {
      return messages
    }
    return messages.filter((item) => item.type === activeTab)
  }, [activeTab])

  const login = async () => {
    try {
      setLoading(true)
      const loginUser = await authApi.ensureLogin()
      setUser(loginUser)
      authApi.getMe().then(setUser).catch(() => {})
    } finally {
      setLoading(false)
    }
  }

  const goQuestionnaire = () => {
    Taro.navigateTo({ url: '/pages/questionnaire/index' })
  }

  const openMessage = (url: string) => {
    if (url.includes('/profile/index')) {
      Taro.switchTab({ url })
      return
    }
    Taro.navigateTo({ url })
  }

  const renderMessageList = () => (
    <>
      <View className="message-tabs">
        {tabs.map((tab) => (
          <View
            className={activeTab === tab.type ? 'message-tab message-tab-active' : 'message-tab'}
            key={tab.type}
            onClick={() => setActiveTab(tab.type)}
          >
            <Text className="message-tab-text">{tab.label}</Text>
          </View>
        ))}
      </View>

      <View className="message-list">
        {filteredMessages.map((item) => (
          <View className="message-item" key={item.id} hoverClass="message-item-hover" onClick={() => openMessage(item.url)}>
            <View className="message-icon">
              <Text className="message-icon-text">{item.icon}</Text>
              {item.unread ? <View className="message-dot" /> : null}
            </View>
            <View className="message-copy">
              <View className="message-line">
                <Text className="message-name">{item.title}</Text>
                <Text className="message-time">{item.time}</Text>
              </View>
              <Text className="message-desc">{item.desc}</Text>
            </View>
            <Text className="message-arrow">›</Text>
          </View>
        ))}
      </View>
    </>
  )

  const renderEmptyState = () => {
    if (!user) {
      return (
        <View className="message-empty">
          <View className="message-empty-icon">
            <Text className="message-empty-icon-text">⌁</Text>
          </View>
          <Text className="message-empty-title">登录后查看消息</Text>
          <Text className="message-empty-desc">登录后可同步你的测评结果、服务需求和顾问回复。</Text>
          <View className="message-empty-action">
            <AppButton text="微信登录" loading={loading} disabled={loading} onClick={login} />
          </View>
        </View>
      )
    }

    return (
      <View className="message-empty">
        <View className="message-empty-icon">
          <Text className="message-empty-icon-text">✓</Text>
        </View>
        <Text className="message-empty-title">暂无消息</Text>
        <Text className="message-empty-desc">完成电费瘦身小测试后，报告、服务进度和顾问回复会在这里同步。</Text>
        <View className="message-empty-action">
          <AppButton text="去做测试" onClick={goQuestionnaire} />
        </View>
      </View>
    )
  }

  return (
    <View className="messages-page">
      <Text className="messages-title">消息</Text>
      {messages.length > 0 ? renderMessageList() : renderEmptyState()}
    </View>
  )
}
