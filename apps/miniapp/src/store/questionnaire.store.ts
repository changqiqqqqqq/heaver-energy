import Taro from '@tarojs/taro'

import type { QuestionnaireResponse, QuestionnaireSubmissionResponse } from '@/services/questionnaire.api'

export type AnswerDraft = Record<number, number[]>

export type QuestionnaireState = {
  questionnaire?: QuestionnaireResponse
  answers: AnswerDraft
  submission?: QuestionnaireSubmissionResponse
}

export const initialQuestionnaireState: QuestionnaireState = {
  answers: {},
}

const DRAFT_KEY = 'heaver.questionnaire_draft'
const RESULT_KEY = 'heaver.latest_submission'

export const saveAnswerDraft = (answers: AnswerDraft) => {
  Taro.setStorageSync(DRAFT_KEY, answers)
}

export const loadAnswerDraft = (): AnswerDraft => {
  return Taro.getStorageSync<AnswerDraft>(DRAFT_KEY) || {}
}

export const clearAnswerDraft = () => {
  Taro.removeStorageSync(DRAFT_KEY)
}

export const saveLatestSubmission = (submission: QuestionnaireSubmissionResponse) => {
  Taro.setStorageSync(RESULT_KEY, submission)
}

export const getLatestSubmission = (): QuestionnaireSubmissionResponse | undefined => {
  return Taro.getStorageSync<QuestionnaireSubmissionResponse>(RESULT_KEY) || undefined
}
