import { Text, Textarea, View } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useMemo, useState } from 'react'

import AppButton from '@/components/AppButton'
import PrivacyPanel from '@/components/PrivacyPanel'
import { authApi } from '@/services/auth.api'
import { serviceRequestApi, type NeedType } from '@/services/service-request.api'
import { normalizeText } from '@/utils/validators'

import './index.css'

type NeedOption = {
  type: NeedType
  name: string
  title: string
  copy: string
}

const needOptions: NeedOption[] = [
  {
    type: 'energy_consulting',
    name: '商电成本核查',
    title: '我想先看降本空间',
    copy: '适合电费持续偏高、想知道有没有优化余地的企业。',
  },
  {
    type: 'quote_review',
    name: '报价方案判断',
    title: '帮我看报价是否合理',
    copy: '适合已经拿到售电、绿电、储能或综合能源报价的企业。',
  },
  {
    type: 'supplier_recommendation',
    name: '供应商筛选',
    title: '我需要筛选供应商',
    copy: '适合不知道如何对比服务商、担心合同和履约风险的企业。',
  },
  {
    type: 'solar_storage',
    name: '光储方案初评',
    title: '想了解光伏/储能',
    copy: '适合有厂房屋顶、峰谷价差或负荷管理需求的企业。',
  },
]

const getQuery = (key: string) => {
  const params = Taro.getCurrentInstance().router?.params || {}
  const value = params[key]
  return typeof value === 'string' ? value : ''
}

const getNumberQuery = (key: string) => {
  const value = Number(getQuery(key))
  return Number.isFinite(value) && value > 0 ? value : undefined
}

export default function ServiceRequestPage() {
  const [selectedType, setSelectedType] = useState<NeedType>('energy_consulting')
  const [description, setDescription] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const profileCode = useMemo(() => getQuery('profileCode'), [])
  const selectedNeed = needOptions.find((item) => item.type === selectedType) || needOptions[0]

  const submit = async () => {
    try {
      setSubmitting(true)
      await authApi.ensureLogin()
      const response = await serviceRequestApi.submit({
        lead_id: getNumberQuery('leadId'),
        submission_id: getNumberQuery('submissionId'),
        primary_need_type: selectedNeed.type,
        description: normalizeText(description),
        items: [
          {
            need_type: selectedNeed.type,
            need_name: selectedNeed.name,
            extra: {
              profile_code: profileCode,
              source: 'miniapp_mvp_service_request',
            },
          },
        ],
      })

      Taro.showToast({ title: '已提交需求', icon: 'success' })
      setTimeout(() => {
        Taro.redirectTo({
          url: `/pages/chat/index?serviceRequestId=${response.id}&requestNo=${response.request_no}`,
        })
      }, 600)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <View className="service-page">
      <View className="service-header">
        <Text className="service-back" onClick={() => Taro.navigateBack()}>
          ‹
        </Text>
        <Text className="service-title">顾问咨询</Text>
      </View>

      <View className="service-hero">
        <Text className="service-hero-title">把你的问题交给顾问判断</Text>
        <Text className="service-hero-copy">从电费、报价、供应商、光储方案里选一个最关心的问题，我们会按线索优先级承接。</Text>
      </View>

      <View className="need-list">
        <Text className="need-section-title">最想解决什么</Text>
        {needOptions.map((item) => (
          <View
            key={item.type}
            className={item.type === selectedType ? 'need-card need-card-active' : 'need-card'}
            hoverClass="need-card-hover"
            onClick={() => setSelectedType(item.type)}
          >
            <View className="need-icon">
              <Text className="need-icon-text">{item.type === selectedType ? '✓' : '○'}</Text>
            </View>
            <View className="need-copy">
              <Text className="need-title">{item.title}</Text>
              <Text className="need-desc">{item.copy}</Text>
            </View>
          </View>
        ))}
      </View>

      <View className="service-note">
        <Text className="service-note-title">补充说明</Text>
        <Textarea
          className="service-textarea"
          maxlength={500}
          placeholder="可填写企业现状、近期报价、电费账单异常或希望顾问重点看的问题"
          placeholderClass="service-placeholder"
          value={description}
          onInput={(event) => setDescription(event.detail.value)}
        />
      </View>

      <View className="service-submit">
        <AppButton text="确认提交" loading={submitting} disabled={submitting} onClick={submit} />
      </View>

      <View className="service-process">
        <Text className="process-title">提交后会发生什么</Text>
        <Text className="process-line">1. 系统生成服务需求单</Text>
        <Text className="process-line">2. 顾问查看测评结果和你的补充说明</Text>
        <Text className="process-line">3. 后续通过消息页同步处理进展</Text>
      </View>

      <PrivacyPanel />
    </View>
  )
}

