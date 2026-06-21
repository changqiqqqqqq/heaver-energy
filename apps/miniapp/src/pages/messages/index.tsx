import { Text, View } from '@tarojs/components'
import Taro from '@tarojs/taro'

import './index.css'

const tabs = ['全部', '通知', '服务进度']

const messages = [
  {
    id: 'consultant',
    icon: '⌁',
    title: '李师傅 顾问',
    time: '刚刚',
    desc: '收到了你的经营体质画像，请补充企业信息，我帮你做初筛。',
    unread: true,
    url: '/pages/chat/index',
  },
  {
    id: 'progress',
    icon: '▤',
    title: '免费优化报告',
    time: '09:15',
    desc: '你的专属报告已进入资料补充阶段，提交后会生成服务进度。',
    unread: false,
    url: '/pages/screening/index',
  },
  {
    id: 'notice',
    icon: '!',
    title: '服务通知',
    time: '昨天',
    desc: '账单上传通道即将开放，当前可先提交基础信息完成初筛。',
    unread: false,
    url: '/pages/chat/index',
  },
  {
    id: 'system',
    icon: '□',
    title: '系统消息',
    time: '周一',
    desc: '测评结果已生成，可在「我的」里查看最近一次画像。',
    unread: false,
    url: '/pages/profile/index',
  },
]

export default function MessagesPage() {
  const openMessage = (url: string) => {
    if (url.includes('/profile/index')) {
      Taro.switchTab({ url })
      return
    }
    Taro.navigateTo({ url })
  }

  return (
    <View className="messages-page">
      <Text className="messages-title">消息</Text>

      <View className="message-tabs">
        {tabs.map((tab, index) => (
          <View className={index === 0 ? 'message-tab message-tab-active' : 'message-tab'} key={tab}>
            <Text className="message-tab-text">{tab}</Text>
          </View>
        ))}
      </View>

      <View className="message-list">
        {messages.map((item) => (
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
    </View>
  )
}
