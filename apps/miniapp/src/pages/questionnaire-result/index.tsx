import { Text, View } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useEffect, useState } from 'react'

import AppButton from '@/components/AppButton'
import { authApi } from '@/services/auth.api'
import { questionnaireApi, type QuestionnaireSubmissionResponse } from '@/services/questionnaire.api'
import { getLatestSubmission, saveLatestSubmission } from '@/store/questionnaire.store'

import { getResultContent, type ResultAction, type ResultSignal } from './result-content'
import './index.css'

const RESULT_PAGE_VERTICAL_PADDING_RPX = 72
const RESULT_CONTENT_HEIGHT_RPX = 2580
const RESULT_MIN_SCALE = 0.46
const RESULT_DEFAULT_SCALE = 0.62

const clampResultScale = (scale: number) => {
  if (!Number.isFinite(scale)) {
    return RESULT_DEFAULT_SCALE
  }

  return Math.min(1, Math.max(RESULT_MIN_SCALE, Number(scale.toFixed(3))))
}

const getWindowMetrics = () => {
  const { windowHeight, windowWidth } = Taro.getSystemInfoSync()
  if (!windowHeight || !windowWidth) {
    return undefined
  }

  return {
    windowWidth,
    availableHeightRpx: (windowHeight * 750) / windowWidth - RESULT_PAGE_VERTICAL_PADDING_RPX,
  }
}

// 先按窗口高度给出兜底比例，真机渲染后会再用实际内容高度校准一次。
const getResultFitScale = () => {
  try {
    const metrics = getWindowMetrics()
    if (!metrics) {
      return RESULT_DEFAULT_SCALE
    }

    return clampResultScale(metrics.availableHeightRpx / RESULT_CONTENT_HEIGHT_RPX)
  } catch {
    return RESULT_DEFAULT_SCALE
  }
}

const getQueryId = () => {
  const params = Taro.getCurrentInstance().router?.params || {}
  const value = params.submissionId
  return value ? Number(value) : undefined
}

const buildActionUrl = (action: ResultAction, submission: QuestionnaireSubmissionResponse) => {
  const query = `leadId=${submission.lead_id || ''}&submissionId=${submission.id || ''}&profileCode=${submission.profile_code || ''}`
  return action.type === 'report' ? `/pages/screening/index?${query}` : `/pages/service-request/index?${query}`
}

function SignalCopy({ signal }: { signal: ResultSignal }) {
  return (
    <Text className="result-signal-copy">
      {signal.prefix}
      <Text className="result-highlight">{signal.highlight}</Text>
      {signal.suffix}
    </Text>
  )
}

export default function QuestionnaireResultPage() {
  const [submission, setSubmission] = useState<QuestionnaireSubmissionResponse | undefined>(() => getLatestSubmission())
  const [loading, setLoading] = useState(false)
  const [resultScale, setResultScale] = useState(() => getResultFitScale())

  useEffect(() => {
    setResultScale(getResultFitScale())
  }, [submission?.id])

  useEffect(() => {
    if (!submission) {
      return
    }

    const timer = setTimeout(() => {
      try {
        const metrics = getWindowMetrics()
        if (!metrics) {
          return
        }

        Taro.createSelectorQuery()
          .select('.result-fit')
          .boundingClientRect((rectResult) => {
            const rect = Array.isArray(rectResult) ? rectResult[0] : rectResult
            if (!rect?.height) {
              return
            }

            const renderedHeightRpx = (rect.height * 750) / metrics.windowWidth
            const naturalHeightRpx = renderedHeightRpx / resultScale
            const nextScale = clampResultScale(metrics.availableHeightRpx / naturalHeightRpx)
            if (Math.abs(nextScale - resultScale) > 0.01) {
              setResultScale(nextScale)
            }
          })
          .exec()
      } catch {
        setResultScale(getResultFitScale())
      }
    }, 80)

    return () => clearTimeout(timer)
  }, [resultScale, submission?.id])

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
      } catch {
        Taro.showToast({ title: '结果读取失败，请稍后重试', icon: 'none' })
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [submission?.id])

  if (loading || !submission) {
    return (
      <View className="result-page result-center result-theme-flame">
        <Text className="result-loading">{loading ? '正在读取结果...' : '暂无测评结果'}</Text>
        {!loading ? (
          <View className="result-empty-action">
            <AppButton text="去做测试" onClick={() => Taro.redirectTo({ url: '/pages/questionnaire/index' })} />
          </View>
        ) : null}
      </View>
    )
  }

  const content = getResultContent(submission.profile_code)
  const fitWidthPercent = 100 / resultScale

  return (
    <View className={`result-page result-theme-${content.theme}`}>
      <View
        className="result-fit"
        style={{
          width: `${fitWidthPercent}%`,
          marginLeft: `${(100 - fitWidthPercent) / 2}%`,
          transform: `scale(${resultScale})`,
        }}
      >
        <View className="result-bg-art">
          <View className="result-bg-line result-bg-line-a" />
          <View className="result-bg-line result-bg-line-b" />
          <View className="result-bg-bar result-bg-bar-a" />
          <View className="result-bg-bar result-bg-bar-b" />
          <View className="result-bg-bar result-bg-bar-c" />
        </View>

        <View className="result-status" />

        <View className="result-header">
          <View className="result-icon-box">
            <Text className="result-icon-text">{content.icon}</Text>
          </View>
          <View className="result-title-row">
            <View className="result-title-mark" />
            <Text className="result-title">{content.title}</Text>
            <View className="result-title-mark result-title-mark-right" />
          </View>
          <View className="result-subtitle-row">
            <View className="result-subtitle-line" />
            <Text className="result-subtitle">{content.subtitle}</Text>
            <View className="result-subtitle-line result-subtitle-line-right" />
          </View>
        </View>

        <View className="result-main-card">
          <Text className="result-stat-num">{content.stat}</Text>
          <Text className="result-stat-label">{content.statLabel}</Text>

          <View className="result-signal-list">
            {content.signals.map((signal, index) => (
              <View className="result-signal-item" key={signal.highlight}>
                <View className="result-num-badge">
                  <Text className="result-num-text">{index + 1}</Text>
                </View>
                <SignalCopy signal={signal} />
                <View className="result-mini-icon">
                  <Text className="result-mini-icon-text">{signal.icon}</Text>
                </View>
              </View>
            ))}
          </View>

          <View className="result-warn-box">
            <View className="result-warn-icon">
              <Text className="result-warn-icon-text">!</Text>
            </View>
            <Text className="result-warn-text">{content.warning}</Text>
          </View>
        </View>

        <View className="result-actions">
          <View className="result-action result-action-secondary" hoverClass="result-tap" onClick={() => Taro.navigateTo({ url: '/pages/share-card/index' })}>
            <Text className="result-action-icon">↓</Text>
            <Text className="result-action-text">保存</Text>
          </View>
          <View className="result-action result-action-primary" hoverClass="result-tap" onClick={() => Taro.navigateTo({ url: '/pages/share-card/index' })}>
            <Text className="result-action-icon">↗</Text>
            <Text className="result-action-text">分享</Text>
          </View>
        </View>

        <View className="result-next-section">
          <Text className="result-next-label">接下来，你想做什么？</Text>
          <View className="result-next-list">
            {content.nextActions.map((action) => (
              <View className="result-next-row" hoverClass="result-tap" key={action.title} onClick={() => Taro.navigateTo({ url: buildActionUrl(action, submission) })}>
                <View className="result-next-icon">
                  <Text className="result-next-icon-text">{action.icon}</Text>
                </View>
                <View className="result-next-copy">
                  <Text className="result-next-title">{action.title}</Text>
                  <Text className="result-next-subtitle">{action.subtitle}</Text>
                </View>
                <Text className="result-next-arrow">›</Text>
              </View>
            ))}
          </View>
        </View>

        <Text className="result-footer-note">{content.footerNote}</Text>
      </View>
    </View>
  )
}
