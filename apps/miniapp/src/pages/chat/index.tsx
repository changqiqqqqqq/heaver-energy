import { Text, Textarea, View } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useMemo } from 'react'

import AppButton from '@/components/AppButton'

import './index.css'

const getQuery = (key: string) => {
  const params = Taro.getCurrentInstance().router?.params || {}
  const value = params[key]
  return typeof value === 'string' ? value : ''
}

export default function ChatPage() {
  const requestNo = useMemo(() => getQuery('requestNo'), [])
  const screeningId = useMemo(() => getQuery('screeningId'), [])

  return (
    <View className="chat-page">
      <View className="chat-header">
        <Text className="chat-back" onClick={() => Taro.navigateBack()}>
          ‹
        </Text>
        <View className="chat-person">
          <View className="chat-avatar">
            <Text className="chat-avatar-text">⌁</Text>
          </View>
          <View>
            <Text className="chat-name">能源顾问</Text>
            <Text className="chat-status">工作日 9:00-18:00 响应</Text>
          </View>
        </View>
      </View>

      <View className="chat-body">
        <View className="bubble bubble-bot">
          <Text className="bubble-text">你好，我已经收到你的信息。可以先补充企业信息或提交具体问题，我会按服务单跟进。</Text>
        </View>

        {requestNo ? (
          <View className="service-status-card">
            <Text className="status-title">服务需求已创建</Text>
            <Text className="status-no">单号：{requestNo}</Text>
            <Text className="status-desc">顾问会结合你的测评结果判断下一步处理方式。</Text>
          </View>
        ) : null}

        {screeningId ? (
          <View className="service-status-card">
            <Text className="status-title">免费初筛已提交</Text>
            <Text className="status-no">初筛编号：{screeningId}</Text>
            <Text className="status-desc">我们会基于企业信息生成初步优化建议。</Text>
          </View>
        ) : null}

        <View className="bubble bubble-user">
          <Text className="bubble-text">我想看看企业电费还有没有优化空间。</Text>
        </View>

        <View className="quick-actions">
          <View className="quick-action" onClick={() => Taro.navigateTo({ url: '/pages/screening/index' })}>
            <Text className="quick-action-title">补充企业信息</Text>
            <Text className="quick-action-copy">领取免费优化报告</Text>
          </View>
          <View className="quick-action" onClick={() => Taro.navigateTo({ url: '/pages/service-request/index' })}>
            <Text className="quick-action-title">提交具体需求</Text>
            <Text className="quick-action-copy">报价、供应商、光储方案</Text>
          </View>
        </View>
      </View>

      <View className="chat-input-panel">
        <Textarea
          className="chat-input"
          disabled
          placeholder="在线客服输入能力待接入，当前请使用上方快捷入口"
          placeholderClass="chat-placeholder"
        />
        <View className="chat-send">
          <AppButton text="提交需求" onClick={() => Taro.navigateTo({ url: '/pages/service-request/index' })} />
        </View>
      </View>
    </View>
  )
}
