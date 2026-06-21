import { APP_API_PREFIX, request } from '@/services/http'

export type QuestionnaireOption = {
  id: number
  option_label?: string | null
  title: string
  subtitle?: string | null
  sort_order: number
}

export type QuestionnaireQuestion = {
  id: number
  question_code?: string | null
  title: string
  subtitle?: string | null
  dimension_code?: string | null
  question_type: 'single_choice' | 'multiple_choice'
  score_mode: 'score' | 'tag_only'
  sort_order: number
  is_required: boolean
  options: QuestionnaireOption[]
}

export type QuestionnaireProfile = {
  profile_code: string
  profile_name: string
  lead_grade_suggestion?: string | null
  theme_color?: string | null
  tags: string[]
  summary?: string | null
  recommendations: string[]
  result_page?: {
    headline?: string | null
    benchmark?: string | null
    benchmark_source?: string | null
    signals: string[]
    cta: Record<string, unknown>
    disclaimer?: string | null
  } | null
}

export type QuestionnaireResponse = {
  id: number
  code: string
  name: string
  version: string
  description?: string | null
  status: string
  questions: QuestionnaireQuestion[]
  profiles: QuestionnaireProfile[]
}

export type QuestionnaireSubmissionResponse = {
  id: number
  questionnaire_id: number
  lead_id: number | null
  profile_code: string | null
  profile_name: string | null
  lead_grade: 'A' | 'B' | 'C' | 'D' | null
  total_score: number
  dimension_scores: Record<string, number>
  dimension_stars: Record<string, number>
  answer_tags: Record<string, unknown>
  result: QuestionnaireProfile | null
  answers_snapshot: Array<Record<string, unknown>>
}

export type QuestionnaireAnswerPayload = {
  question_id: number
  option_ids: number[]
}

export const questionnaireApi = {
  getCurrent(code = 'business_health') {
    return request<QuestionnaireResponse>({
      url: `${APP_API_PREFIX}/questionnaires/current?code=${encodeURIComponent(code)}`,
      auth: false,
    })
  },

  submit(questionnaireId: number, answers: QuestionnaireAnswerPayload[], leadId?: number | null) {
    return request<QuestionnaireSubmissionResponse>({
      url: `${APP_API_PREFIX}/questionnaires/${questionnaireId}/submissions`,
      method: 'POST',
      data: {
        lead_id: leadId || null,
        answers,
      },
    })
  },

  getSubmission(submissionId: number) {
    return request<QuestionnaireSubmissionResponse>({
      url: `${APP_API_PREFIX}/questionnaires/submissions/${submissionId}`,
    })
  },
}
