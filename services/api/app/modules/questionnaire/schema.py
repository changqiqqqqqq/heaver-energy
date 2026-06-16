"""测评题库与答题接口模型。"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class QuestionnaireOptionResponse(BaseModel):
    id: int
    option_label: str | None = None
    title: str
    subtitle: str | None = None
    sort_order: int

    model_config = ConfigDict(from_attributes=True)


class QuestionnaireQuestionResponse(BaseModel):
    id: int
    title: str
    subtitle: str | None = None
    dimension_code: str | None = None
    question_type: str
    sort_order: int
    is_required: bool
    options: list[QuestionnaireOptionResponse]

    model_config = ConfigDict(from_attributes=True)


class QuestionnaireProfileResponse(BaseModel):
    profile_code: str
    profile_name: str
    lead_grade_suggestion: str | None = None
    theme_color: str | None = None
    tags: list[str] = Field(default_factory=list)
    summary: str | None = None
    recommendations: list[str] = Field(default_factory=list)


class QuestionnaireResponse(BaseModel):
    id: int
    code: str
    name: str
    version: str
    description: str | None = None
    status: str
    questions: list[QuestionnaireQuestionResponse]
    profiles: list[QuestionnaireProfileResponse] = Field(default_factory=list)


class QuestionnaireAnswerRequest(BaseModel):
    question_id: int
    option_ids: list[int] = Field(min_length=1)


class QuestionnaireSubmitRequest(BaseModel):
    enterprise_id: int | None = None
    lead_id: int | None = None
    answers: list[QuestionnaireAnswerRequest] = Field(min_length=1)


class QuestionnaireSubmissionResponse(BaseModel):
    id: int
    questionnaire_id: int
    profile_code: str | None
    profile_name: str | None
    total_score: int
    dimension_scores: dict[str, int]
    result: QuestionnaireProfileResponse | None
    answers_snapshot: list[dict[str, Any]]


class AdminQuestionnaireOptionInput(BaseModel):
    option_label: str | None = Field(default=None, max_length=8)
    title: str = Field(min_length=1, max_length=256)
    subtitle: str | None = Field(default=None, max_length=256)
    score_json: dict[str, int] | None = None
    profile_bias: str | None = Field(default=None, max_length=64)
    sort_order: int = 0


class AdminQuestionnaireQuestionInput(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    subtitle: str | None = Field(default=None, max_length=256)
    dimension_code: str | None = Field(default=None, max_length=64)
    question_type: str = Field(default="single_choice", pattern="^(single_choice|multiple_choice)$")
    sort_order: int = 0
    is_required: bool = True
    options: list[AdminQuestionnaireOptionInput] = Field(min_length=1)


class AdminQuestionnaireProfileInput(BaseModel):
    profile_code: str = Field(min_length=1, max_length=64)
    profile_name: str = Field(min_length=1, max_length=64)
    lead_grade_suggestion: str | None = Field(default=None, max_length=16)
    theme_color: str | None = Field(default=None, max_length=32)
    tags: list[str] = Field(default_factory=list)
    summary: str | None = Field(default=None, max_length=512)
    recommendations: list[str] = Field(default_factory=list)
    rule_json: dict[str, Any] | None = None


class AdminQuestionnaireCreateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=128)
    version: str = Field(default="v1", max_length=32)
    description: str | None = Field(default=None, max_length=512)
    status: str = Field(default="draft", pattern="^(draft|published|archived)$")
    questions: list[AdminQuestionnaireQuestionInput] = Field(min_length=1)
    profiles: list[AdminQuestionnaireProfileInput] = Field(default_factory=list)


class AdminQuestionnaireListItem(BaseModel):
    id: int
    code: str
    name: str
    version: str
    status: str

    model_config = ConfigDict(from_attributes=True)
