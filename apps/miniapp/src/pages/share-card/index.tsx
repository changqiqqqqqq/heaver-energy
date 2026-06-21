import { Button, Text, View } from '@tarojs/components'
import Taro, { useShareAppMessage } from '@tarojs/taro'
import { useMemo } from 'react'

import AppButton from '@/components/AppButton'
import { getLatestSubmission } from '@/store/questionnaire.store'

import './index.css'

const profileThemes: Record<string, 'orange' | 'blue' | 'green'> = {
  hidden_waste: 'orange',
  cost_sensitive: 'orange',
  supplier_confused: 'orange',
  growth_expansion: 'blue',
  energy_awakened: 'blue',
  stable_operation: 'green',
}

const dimensionNames: Record<string, string> = {
  CP: '成本',
  MA: '管理',
  SR: '供应商',
  EP: '优化',
  AM: '行动',
  LV: '线索',
}

export default function ShareCardPage() {
  const submission = useMemo(() => getLatestSubmission(), [])
  const theme = profileThemes[submission?.profile_code || ''] || 'orange'
  const profileName = submission?.profile_name || submission?.result?.profile_name || '经营体质画像'
  const summary = submission?.result?.summary || submission?.result?.result_page?.headline || '完成电费经营体质测试，看看你的企业还有多少优化空间。'
  const dimensionList = Object.entries(submission?.dimension_stars || {}).slice(0, 4)

  useShareAppMessage(() => ({
    title: `我的商电经营体质：${profileName}`,
    path: '/pages/home/index',
  }))

  const saveCard = () => {
    // 小程序端真实海报保存需要 canvas 生成图片，这里先提供原型阶段可用的截图保存路径。
    Taro.showToast({ title: '可长按截图保存分享卡', icon: 'none' })
  }

  if (!submission) {
    return (
      <View className="share-page share-center">
        <Text className="share-empty-title">还没有可分享的结果</Text>
        <View className="share-empty-action">
          <AppButton text="去做测试" onClick={() => Taro.redirectTo({ url: '/pages/questionnaire/index' })} />
        </View>
      </View>
    )
  }

  return (
    <View className={`share-page share-theme-${theme}`}>
      <View className="share-card">
        <View className="share-brand">
          <View className="share-brand-mark">
            <Text className="share-brand-face">⌁</Text>
          </View>
          <Text className="share-brand-name">河狸数字能源</Text>
        </View>

        <View className="share-icon">
          <Text className="share-icon-text">♙</Text>
        </View>
        <Text className="share-kicker">经营体质画像 2026</Text>
        <Text className="share-profile">{profileName}</Text>
        <Text className="share-summary">{summary}</Text>

        <View className="share-tags">
          <Text className="share-tag">线索等级 {submission.lead_grade || '-'}</Text>
          <Text className="share-tag">1分钟测完</Text>
        </View>

        <View className="share-divider" />

        <View className="share-bottom">
          <View className="share-bottom-copy">
            <Text className="share-bottom-title">免费领取商电优化方案</Text>
            <Text className="share-bottom-desc">扫码测一测，先看企业电费是否有优化空间</Text>
          </View>
          <View className="share-qr">
            <View className="qr-line qr-line-one" />
            <View className="qr-line qr-line-two" />
            <View className="qr-line qr-line-three" />
          </View>
        </View>
      </View>

      <View className="share-dimension">
        {dimensionList.map(([code, stars]) => (
          <View className="share-dimension-item" key={code}>
            <Text className="share-dimension-name">{dimensionNames[code] || code}</Text>
            <Text className="share-dimension-score">{stars}/5</Text>
          </View>
        ))}
      </View>

      <View className="share-actions">
        <View className="share-action-item">
          <AppButton text="保存卡片" variant="light" onClick={saveCard} />
        </View>
        <Button className="share-native-button" openType="share">
          分享给朋友
        </Button>
      </View>
    </View>
  )
}

