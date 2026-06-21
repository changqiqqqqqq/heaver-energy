import { Text, View } from '@tarojs/components'

import './index.css'

export default function PrivacyPanel() {
  return (
    <View className="privacy-panel">
      <Text className="privacy-title">隐私与数据说明</Text>
      <Text className="privacy-copy">测评结果仅用于生成经营体质建议和后续服务承接。手机号、账单等敏感信息会按后端规则脱敏保存。</Text>
    </View>
  )
}
