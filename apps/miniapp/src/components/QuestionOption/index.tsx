import { Text, View } from '@tarojs/components'

import type { QuestionnaireOption } from '@/services/questionnaire.api'

import './index.css'

type QuestionOptionProps = {
  option: QuestionnaireOption
  active: boolean
  onSelect: () => void
}

export default function QuestionOption({ option, active, onSelect }: QuestionOptionProps) {
  return (
    <View className={`question-option ${active ? 'question-option-active' : ''}`} hoverClass="question-option-hover" onClick={onSelect}>
      <View className="question-option-badge">
        <Text className="question-option-badge-text">{option.option_label || '选'}</Text>
      </View>
      <View className="question-option-content">
        <Text className="question-option-title">{option.title}</Text>
        {option.subtitle ? <Text className="question-option-subtitle">{option.subtitle}</Text> : null}
      </View>
      <Text className="question-option-arrow">{active ? '✓' : '›'}</Text>
    </View>
  )
}
