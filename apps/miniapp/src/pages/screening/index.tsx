import { Input, Picker, Text, View } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useMemo, useState } from 'react'

import AppButton from '@/components/AppButton'
import PrivacyPanel from '@/components/PrivacyPanel'
import UploadBill from '@/components/UploadBill'
import { authApi } from '@/services/auth.api'
import { screeningApi } from '@/services/screening.api'
import { isChinaMobile, normalizeText } from '@/utils/validators'

import './index.css'

type ScreeningForm = {
  enterprise_name: string
  region_text: string
  enterprise_type: string
  monthly_kwh_range: string
  contact_name: string
  contact_phone: string
}

const enterpriseTypes = ['制造业', '商业综合体', '园区/物业', '连锁门店', '办公写字楼', '其他']
const kwhRanges = ['1万度以下', '1万-10万度', '10万-50万度', '50万度以上', '暂不确定']

const initialForm: ScreeningForm = {
  enterprise_name: '',
  region_text: '',
  enterprise_type: '',
  monthly_kwh_range: '',
  contact_name: '',
  contact_phone: '',
}

const getQuery = (key: string) => {
  const params = Taro.getCurrentInstance().router?.params || {}
  const value = params[key]
  return typeof value === 'string' ? value : ''
}

const getNumberQuery = (key: string) => {
  const value = Number(getQuery(key))
  return Number.isFinite(value) && value > 0 ? value : undefined
}

export default function ScreeningPage() {
  const [form, setForm] = useState<ScreeningForm>(initialForm)
  const [submitting, setSubmitting] = useState(false)
  const profileCode = useMemo(() => getQuery('profileCode'), [])

  const updateForm = (field: keyof ScreeningForm, value: string) => {
    setForm((current) => ({
      ...current,
      [field]: value,
    }))
  }

  const validate = () => {
    if (!normalizeText(form.enterprise_name)) {
      Taro.showToast({ title: '请填写企业名称', icon: 'none' })
      return false
    }
    if (!normalizeText(form.region_text)) {
      Taro.showToast({ title: '请填写所在地区', icon: 'none' })
      return false
    }
    if (!normalizeText(form.contact_name)) {
      Taro.showToast({ title: '请填写联系人', icon: 'none' })
      return false
    }
    if (!isChinaMobile(form.contact_phone)) {
      Taro.showToast({ title: '请填写正确手机号', icon: 'none' })
      return false
    }
    return true
  }

  const submit = async () => {
    if (!validate()) {
      return
    }

    try {
      setSubmitting(true)
      await authApi.ensureLogin()
      const response = await screeningApi.submit({
        lead_id: getNumberQuery('leadId'),
        submission_id: getNumberQuery('submissionId'),
        enterprise_name: normalizeText(form.enterprise_name),
        region_text: normalizeText(form.region_text),
        enterprise_type: form.enterprise_type,
        monthly_kwh_range: form.monthly_kwh_range,
        contact_name: normalizeText(form.contact_name),
        contact_phone: normalizeText(form.contact_phone),
        extra: {
          profile_code: profileCode,
          source: 'miniapp_mvp_screening',
        },
      })

      Taro.showToast({ title: '已提交初筛', icon: 'success' })
      setTimeout(() => {
        Taro.redirectTo({
          url: `/pages/chat/index?leadId=${response.lead_id || ''}&screeningId=${response.id}`,
        })
      }, 600)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <View className="screening-page">
      <View className="screening-header">
        <Text className="screening-back" onClick={() => Taro.navigateBack()}>
          ‹
        </Text>
        <Text className="screening-title">领取专属商电优化报告</Text>
      </View>

      <View className="screening-hero">
        <Text className="screening-hero-kicker">免费初筛 · 免账单模板</Text>
        <Text className="screening-hero-title">你的电费降本空间可能超出想象</Text>
        <Text className="screening-hero-copy">留下企业信息，顾问会结合行业、地区与用电规模给出初步优化方向。</Text>
      </View>

      <View className="screening-form">
        <View className="form-section-title">填写信息，免费领取报告</View>

        <View className="form-row">
          <Text className="form-label">企业名称</Text>
          <Input
            className="form-input"
            placeholder="请输入企业名称"
            placeholderClass="form-placeholder"
            value={form.enterprise_name}
            onInput={(event) => updateForm('enterprise_name', event.detail.value)}
          />
        </View>

        <View className="form-row">
          <Text className="form-label">所在地区</Text>
          <Input
            className="form-input"
            placeholder="例如：广东省深圳市"
            placeholderClass="form-placeholder"
            value={form.region_text}
            onInput={(event) => updateForm('region_text', event.detail.value)}
          />
        </View>

        <View className="form-pair">
          <Picker
            mode="selector"
            range={enterpriseTypes}
            onChange={(event) => updateForm('enterprise_type', enterpriseTypes[Number(event.detail.value)] || '')}
          >
            <View className="form-picker">
              <Text className="form-label">企业类型</Text>
              <Text className={form.enterprise_type ? 'form-picker-value' : 'form-picker-placeholder'}>
                {form.enterprise_type || '请选择'}
              </Text>
            </View>
          </Picker>

          <Picker
            mode="selector"
            range={kwhRanges}
            onChange={(event) => updateForm('monthly_kwh_range', kwhRanges[Number(event.detail.value)] || '')}
          >
            <View className="form-picker">
              <Text className="form-label">月用电量</Text>
              <Text className={form.monthly_kwh_range ? 'form-picker-value' : 'form-picker-placeholder'}>
                {form.monthly_kwh_range || '请选择'}
              </Text>
            </View>
          </Picker>
        </View>

        <View className="form-row">
          <Text className="form-label">联系人</Text>
          <Input
            className="form-input"
            placeholder="请输入姓名"
            placeholderClass="form-placeholder"
            value={form.contact_name}
            onInput={(event) => updateForm('contact_name', event.detail.value)}
          />
        </View>

        <View className="form-row">
          <Text className="form-label">联系电话</Text>
          <Input
            className="form-input"
            type="number"
            maxlength={11}
            placeholder="用于接收初筛反馈"
            placeholderClass="form-placeholder"
            value={form.contact_phone}
            onInput={(event) => updateForm('contact_phone', event.detail.value)}
          />
        </View>

        <UploadBill />

        <View className="screening-submit">
          <AppButton text="提交 · 免费初筛" loading={submitting} disabled={submitting} onClick={submit} />
        </View>
      </View>

      <View className="screening-hints">
        <Text className="hint-title">报告包含以下内容</Text>
        <Text className="hint-line">• 企业当前商电经营状态判断</Text>
        <Text className="hint-line">• 可能存在的降本方向与风险点</Text>
        <Text className="hint-line">• 是否适合进一步做账单和合同诊断</Text>
      </View>

      <PrivacyPanel />
    </View>
  )
}

