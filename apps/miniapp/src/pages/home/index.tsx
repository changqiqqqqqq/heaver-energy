import { Image, Text, View } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useEffect } from 'react'

import topLogoIcon from '@/assets/top-logo-icon.png'
import EnergyCard from '@/components/EnergyCard'
import { authApi } from '@/services/auth.api'

import './index.css'

const navigateTo = (url: string) => {
  Taro.navigateTo({ url })
}

export default function HomePage() {
  useEffect(() => {
    // 首页只做静默登录，不阻塞用户开始测评，避免首屏体验被网络状态拖住。
    authApi.ensureLogin().catch(() => undefined)
  }, [])

  return (
    <View className="home-page">
      <View className="home-status" />

      <View className="brand-row">
        <View className="brand-mark">
          <Image className="brand-logo-icon" src={topLogoIcon} mode="aspectFit" />
        </View>
        <View className="brand-copy">
          <Text className="brand-name">河狸数字能源</Text>
          <Text className="brand-slogan">帮你把每度电用得明明白白</Text>
        </View>
      </View>

      <View className="hero-copy">
        <Text className="hero-line">老板</Text>
        <Text className="hero-line">你多交了</Text>
        <Text className="hero-line hero-line-accent">多少电费？</Text>
        <Text className="hero-subtitle">测一测，发现降本空间</Text>
      </View>

      <View className="primary-card" hoverClass="tap-soft" onClick={() => navigateTo('/pages/questionnaire/index')}>
        <View className="primary-icon">
          <View className="target-ring target-ring-outer" />
          <View className="target-ring target-ring-middle" />
          <View className="target-ring target-ring-inner" />
        </View>

        <View className="primary-card-copy">
          <Text className="primary-title">电费瘦身小测试</Text>
          <Text className="primary-subtitle">无需数据 · 问题简单</Text>
        </View>

        <Text className="primary-desc">1分钟，找出你多花的每一分钱。</Text>
        <Text className="primary-link">连接供应商BOSS，直接聊</Text>

        <View className="primary-button">
          <Text className="primary-button-text">戳我开始</Text>
          <Text className="primary-button-arrow">→</Text>
        </View>
      </View>

    </View>
  )
}
