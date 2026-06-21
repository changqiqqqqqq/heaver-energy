import { Text, View } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useEffect, useMemo, useState } from 'react'

import AppButton from '@/components/AppButton'
import EnergyCard from '@/components/EnergyCard'
import { authApi } from '@/services/auth.api'
import { questionnaireApi, type QuestionnaireSubmissionResponse } from '@/services/questionnaire.api'
import { getLatestSubmission, saveLatestSubmission } from '@/store/questionnaire.store'

import './index.css'

const dimensionNames: Record<string, string> = {
  CP: '成本压力',
  MA: '管理清晰度',
  SR: '供应商判断',
  EP: '用能优化',
  AM: '行动成熟度',
  LV: '线索价值',
}

const profileThemes: Record<string, 'orange' | 'blue' | 'green'> = {
  hidden_waste: 'orange',
  cost_sensitive: 'orange',
  supplier_confused: 'orange',
  growth_expansion: 'blue',
  energy_awakened: 'blue',
  stable_operation: 'green',
}

const getQueryId = () => {
  const params = Taro.getCurrentInstance().router?.params || {}
  const value = params.submissionId
  return value ? Number(value) : undefined
}

const getTheme = (profileCode?: string | null) => {
  return profileThemes[profileCode || ''] || 'orange'
}

export default function QuestionnaireResultPage() {
  const [submission, setSubmission] = useState<QuestionnaireSubmissionResponse | undefined>(() => getLatestSubmission())
  const [loading, setLoading] = useState(false)

  const theme = getTheme(submission?.profile_code)
  const result = submission?.result
  const resultPage = result?.result_page
  const dimensionList = useMemo(() => Object.entries(submission?.dimension_stars || {}), [submission])

  useEffect(() => {
    const submissionId = getQueryId()
    if (!submissionId || submission?.id === submissionId) {
      return
    }

    const load = async () => {
      try {
        setLoading(true)
        await authApi.ensureLogin()
        const data = await questionnaireApi.getSubmission(submissionId)
        setSubmission(data)
        saveLatestSubmission(data)
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [submission?.id])

  const goReport = () => {
    Taro.navigateTo({
      url: `/pages/screening/index?leadId=${submission?.lead_id || ''}&submissionId=${submission?.id || ''}&profileCode=${submission?.profile_code || ''}`,
    })
  }

  const goConsult = () => {
    Taro.navigateTo({
      url: `/pages/service-request/index?leadId=${submission?.lead_id || ''}&submissionId=${submission?.id || ''}&profileCode=${submission?.profile_code || ''}`,
    })
  }

  if (loading || !submission) {
    return (
      <View className="result-page result-center">
        <Text className="result-loading">{loading ? '正在读取结果...' : '暂无测评结果'}</Text>
        {!loading ? (
          <View className="result-empty-action">
            <AppButton text="去做测试" onClick={() => Taro.redirectTo({ url: '/pages/questionnaire/index' })} />
          </View>
        ) : null}
      </View>
    )
  }

  return (
    <View className={`result-page result-theme-${theme}`}>
      <View className="result-hero">
        <View className="result-brand">
          <View className="result-brand-mark">
            <Text className="result-brand-face">⌁</Text>
          </View>
          <Text className="result-brand-name">河狸数字能源</Text>
        </View>

        <View className="result-medal">
          <Text className="result-medal-icon">♙</Text>
        </View>
        <Text className="result-label">经营体质画像 2026</Text>
        <Text className="result-profile">{submission.profile_name || result?.profile_name || '经营体质画像'}</Text>
        <Text className="result-summary">{result?.summary || resultPage?.headline || '你已经完成经营体质测试，下一步可以领取更详细的优化建议。'}</Text>

        <View className="result-tags">
          <Text className="result-tag">线索等级 {submission.lead_grade || '-'}</Text>
          <Text className="result-tag">已生成报告</Text>
        </View>

        <View className="result-actions">
          <View className="result-action" onClick={() => Taro.navigateTo({ url: '/pages/share-card/index' })}>
            <Text className="result-action-text">保存</Text>
          </View>
          <View className="result-action result-action-light" onClick={() => Taro.navigateTo({ url: '/pages/share-card/index' })}>
            <Text className="result-action-text">分享</Text>
          </View>
        </View>
      </View>

      <View className="result-section">
        <Text className="result-section-title">接下来，你想做什么？</Text>
        <View className="result-card-list">
          <EnergyCard title="领取专属商电优化报告" subtitle="补充企业信息，获取免费初筛建议" icon="▤" onClick={goReport} />
          <EnergyCard title="我想让顾问帮我看看" subtitle="一对一判断报价、用能或供应商问题" icon="⌘" tone="blue" onClick={goConsult} />
        </View>
      </View>

      <View className="result-section">
        <Text className="result-section-title">你的经营信号</Text>
        <View className="dimension-grid">
          {dimensionList.map(([code, stars]) => (
            <View className="dimension-item" key={code}>
              <Text className="dimension-name">{dimensionNames[code] || code}</Text>
              <View className="dimension-stars">
                {[1, 2, 3, 4, 5].map((value) => (
                  <Text key={value} className={value <= stars ? 'dimension-star dimension-star-on' : 'dimension-star'}>
                    ★
                  </Text>
                ))}
              </View>
            </View>
          ))}
        </View>
      </View>

      {resultPage?.benchmark || resultPage?.signals?.length ? (
        <View className="result-section">
          <Text className="result-section-title">我们看见的机会</Text>
          {resultPage.benchmark ? <Text className="result-benchmark">{resultPage.benchmark}</Text> : null}
          {(resultPage.signals || []).map((signal) => (
            <Text className="result-signal" key={signal}>
              • {signal}
            </Text>
          ))}
        </View>
      ) : null}

      <Text className="result-disclaimer">
        {resultPage?.disclaimer || '以上结果基于问卷答案生成，实际优化空间仍需结合电费账单、合同和企业用能情况进一步判断。'}
      </Text>
    </View>
  )
}
