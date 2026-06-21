import { Text, View } from '@tarojs/components'

import './index.css'

type AppButtonProps = {
  text: string
  variant?: 'primary' | 'light' | 'outline'
  disabled?: boolean
  loading?: boolean
  onClick?: () => void
}

export default function AppButton({ text, variant = 'primary', disabled, loading, onClick }: AppButtonProps) {
  const className = ['app-button', `app-button-${variant}`, disabled ? 'app-button-disabled' : ''].join(' ')

  return (
    <View className={className} hoverClass={disabled ? '' : 'app-button-hover'} onClick={disabled ? undefined : onClick}>
      <Text className="app-button-text">{loading ? '处理中...' : text}</Text>
      {!loading && variant === 'primary' ? <Text className="app-button-arrow">→</Text> : null}
    </View>
  )
}
