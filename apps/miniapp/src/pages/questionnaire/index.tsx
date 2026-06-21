import { Text, View } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useEffect, useMemo, useState } from 'react'

import AppButton from '@/components/AppButton'
import QuestionOption from '@/components/QuestionOption'
import { authApi } from '@/services/auth.api'
import { questionnaireApi, type QuestionnaireQuestion, type QuestionnaireResponse } from '@/services/questionnaire.api'
import { clearAnswerDraft, loadAnswerDraft, saveAnswerDraft, saveLatestSubmission, type AnswerDraft } from '@/store/questionnaire.store'

import './index.css'

const sortQuestions = (questionnaire?: QuestionnaireResponse) => {
  return [...(questionnaire?.questions || [])].sort((a, b) => a.sort_order - b.sort_order)
}

export default function QuestionnairePage() {
  const [questionnaire, setQuestionnaire] = useState<QuestionnaireResponse>()
  const [answers, setAnswers] = useState<AnswerDraft>(() => loadAnswerDraft())
  const [currentIndex, setCurrentIndex] = useState(0)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const questions = useMemo(() => sortQuestions(questionnaire), [questionnaire])
  const currentQuestion = questions[currentIndex]
  const currentAnswer = currentQuestion ? answers[currentQuestion.id] || [] : []
  const progress = questions.length ? Math.round(((currentIndex + 1) / questions.length) * 100) : 0

  useEffect(() => {
    const loadQuestionnaire = async () => {
      try {
        setLoading(true)
        setError('')
        const data = await questionnaireApi.getCurrent('business_health')
        setQuestionnaire(data)
      } catch (err) {
        const message = err instanceof Error ? err.message : '题库加载失败'
        setError(message)
      } finally {
        setLoading(false)
      }
    }

    loadQuestionnaire()
  }, [])

  useEffect(() => {
    saveAnswerDraft(answers)
  }, [answers])

  const selectOption = (question: QuestionnaireQuestion, optionId: number) => {
    const previous = answers[question.id] || []
    const nextValue =
      question.question_type === 'multiple_choice'
        ? previous.includes(optionId)
          ? previous.filter((id) => id !== optionId)
          : [...previous, optionId]
        : [optionId]

    setAnswers({
      ...answers,
      [question.id]: nextValue,
    })
  }

  const validateCurrent = () => {
    if (!currentQuestion) {
      return false
    }
    if (currentQuestion.is_required && currentAnswer.length === 0) {
      Taro.showToast({ title: '请先选择一个答案', icon: 'none' })
      return false
    }
    return true
  }

  const goNext = () => {
    if (!validateCurrent()) {
      return
    }
    setCurrentIndex((value) => Math.min(value + 1, questions.length - 1))
  }

  const goPrev = () => {
    setCurrentIndex((value) => Math.max(value - 1, 0))
  }

  const submit = async () => {
    if (!validateCurrent() || !questionnaire) {
      return
    }

    const missing = questions.find((question) => question.is_required && !(answers[question.id] || []).length)
    if (missing) {
      Taro.showToast({ title: '还有题目未完成', icon: 'none' })
      setCurrentIndex(questions.indexOf(missing))
      return
    }

    try {
      setSubmitting(true)
      await authApi.ensureLogin()
      const result = await questionnaireApi.submit(
        questionnaire.id,
        questions.map((question) => ({
          question_id: question.id,
          option_ids: answers[question.id] || [],
        })),
      )
      clearAnswerDraft()
      saveLatestSubmission(result)
      Taro.redirectTo({ url: `/pages/questionnaire-result/index?submissionId=${result.id}` })
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <View className="quiz-page quiz-center">
        <Text className="quiz-loading">正在准备测试...</Text>
      </View>
    )
  }

  if (error || !currentQuestion) {
    return (
      <View className="quiz-page quiz-center">
        <Text className="quiz-empty-title">暂时没有可用测试</Text>
        <Text className="quiz-empty-copy">{error || '请先在后台发布 business_health 问卷'}</Text>
        <View className="quiz-empty-action">
          <AppButton text="返回首页" onClick={() => Taro.switchTab({ url: '/pages/home/index' })} />
        </View>
      </View>
    )
  }

  const isLast = currentIndex === questions.length - 1

  return (
    <View className="quiz-page">
      <View className="quiz-header">
        <View className="quiz-back" onClick={() => Taro.switchTab({ url: '/pages/home/index' })}>
          <Text className="quiz-back-text">‹</Text>
        </View>
        <View className="quiz-title-block">
          <Text className="quiz-title">电费瘦身小测试</Text>
          <Text className="quiz-count">
            {currentIndex + 1}/{questions.length}
          </Text>
        </View>
      </View>

      <View className="quiz-progress">
        <View className="quiz-progress-fill" style={{ width: `${progress}%` }} />
      </View>

      <View className="question-card">
        <Text className="question-tag">选择最接近你当前情况的一项</Text>
        <Text className="question-title">{currentQuestion.title}</Text>
        {currentQuestion.subtitle ? <Text className="question-subtitle">{currentQuestion.subtitle}</Text> : null}

        <View className="question-options">
          {currentQuestion.options
            .slice()
            .sort((a, b) => a.sort_order - b.sort_order)
            .map((option) => (
              <QuestionOption
                key={option.id}
                option={option}
                active={currentAnswer.includes(option.id)}
                onSelect={() => selectOption(currentQuestion, option.id)}
              />
            ))}
        </View>
      </View>

      <View className="quiz-footer">
        <View className="quiz-prev" onClick={goPrev}>
          <Text className="quiz-prev-text">{currentIndex === 0 ? ' ' : '上一题'}</Text>
        </View>
        <View className="quiz-next">
          <AppButton text={isLast ? '查看结果' : '下一题'} loading={submitting} disabled={submitting} onClick={isLast ? submit : goNext} />
        </View>
      </View>
    </View>
  )
}
