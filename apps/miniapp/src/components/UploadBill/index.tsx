import { Text, View } from '@tarojs/components'
import Taro from '@tarojs/taro'

import './index.css'

type UploadBillProps = {
  disabled?: boolean
}

export default function UploadBill({ disabled }: UploadBillProps) {
  const handleClick = () => {
    // 当前后端只支持文件元数据登记，真实直传能力补齐前先做明确降级提示。
    Taro.showToast({ title: disabled ? '请先提交表单' : '账单上传通道即将开放', icon: 'none' })
  }

  return (
    <View className={`upload-bill ${disabled ? 'upload-bill-disabled' : ''}`} hoverClass="upload-bill-hover" onClick={handleClick}>
      <View className="upload-bill-icon">
        <Text className="upload-bill-icon-text">↥</Text>
      </View>
      <View className="upload-bill-copy">
        <Text className="upload-bill-title">上传电费账单</Text>
        <Text className="upload-bill-subtitle">上传后可进一步判断优化空间</Text>
      </View>
      <Text className="upload-bill-action">PDF/图片</Text>
    </View>
  )
}
