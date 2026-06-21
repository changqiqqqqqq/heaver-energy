import { Text, View } from '@tarojs/components'

import './index.css'

type EnergyCardProps = {
  title: string
  subtitle?: string
  icon?: string
  tone?: 'orange' | 'blue' | 'green'
  onClick?: () => void
}

export default function EnergyCard({ title, subtitle, icon = '⌁', tone = 'orange', onClick }: EnergyCardProps) {
  return (
    <View className={`energy-card energy-card-${tone}`} hoverClass="energy-card-hover" onClick={onClick}>
      <View className="energy-card-icon">
        <Text className="energy-card-icon-text">{icon}</Text>
      </View>
      <View className="energy-card-content">
        <Text className="energy-card-title">{title}</Text>
        {subtitle ? <Text className="energy-card-subtitle">{subtitle}</Text> : null}
      </View>
      <Text className="energy-card-arrow">›</Text>
    </View>
  )
}
