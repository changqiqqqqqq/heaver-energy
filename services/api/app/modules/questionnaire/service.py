"""测评题库与答题业务服务。"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.modules.questionnaire import repository
from app.modules.questionnaire.model import (
    QuestionnaireOption,
    QuestionnaireQuestion,
    QuestionnaireResultProfile,
    QuestionnaireSet,
    QuestionnaireSubmission,
)
from app.modules.questionnaire.schema import (
    AdminQuestionnaireCreateRequest,
    AdminQuestionnaireListItem,
    QuestionnaireOptionResponse,
    QuestionnaireProfileResponse,
    QuestionnaireQuestionResponse,
    QuestionnaireResponse,
    QuestionnaireSubmissionResponse,
    QuestionnaireSubmitRequest,
)
from app.modules.user.model import AppUser


class QuestionnaireServiceError(ValueError):
    """测评业务错误，router 层会转成 HTTP 响应。"""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


@dataclass
class SubmissionCalculation:
    profile: QuestionnaireResultProfile | None
    total_score: int
    dimension_scores: dict[str, int]
    answers_snapshot: list[dict[str, Any]]
    answer_rows: list[dict[str, Any]]
    result_response: QuestionnaireProfileResponse | None


def _profile_response(profile: QuestionnaireResultProfile) -> QuestionnaireProfileResponse:
    return QuestionnaireProfileResponse(
        profile_code=profile.profile_code,
        profile_name=profile.profile_name,
        lead_grade_suggestion=profile.lead_grade_suggestion,
        theme_color=profile.theme_color,
        tags=profile.tags_json or [],
        summary=profile.summary,
        recommendations=profile.recommendations_json or [],
    )


def _question_response(question: QuestionnaireQuestion) -> QuestionnaireQuestionResponse:
    active_options = sorted(question.options, key=lambda option: option.sort_order)
    return QuestionnaireQuestionResponse(
        id=question.id,
        title=question.title,
        subtitle=question.subtitle,
        dimension_code=question.dimension_code,
        question_type=question.question_type,
        sort_order=question.sort_order,
        is_required=question.is_required,
        options=[QuestionnaireOptionResponse.model_validate(option) for option in active_options],
    )


def _questionnaire_response(questionnaire: QuestionnaireSet) -> QuestionnaireResponse:
    active_questions = [
        question
        for question in sorted(questionnaire.questions, key=lambda item: item.sort_order)
        if question.status == "active"
    ]
    return QuestionnaireResponse(
        id=questionnaire.id,
        code=questionnaire.code,
        name=questionnaire.name,
        version=questionnaire.version,
        description=questionnaire.description,
        status=questionnaire.status,
        questions=[_question_response(question) for question in active_questions],
        profiles=[_profile_response(profile) for profile in questionnaire.profiles],
    )


def build_questionnaire_response(questionnaire: QuestionnaireSet) -> QuestionnaireResponse:
    return _questionnaire_response(questionnaire)


def list_admin_questionnaires(db: Session) -> list[AdminQuestionnaireListItem]:
    return [AdminQuestionnaireListItem.model_validate(item) for item in repository.list_questionnaires(db)]


def get_admin_questionnaire(db: Session, questionnaire_id: int) -> QuestionnaireResponse:
    questionnaire = repository.get_questionnaire_detail(db, questionnaire_id)
    if questionnaire is None:
        raise QuestionnaireServiceError("问卷不存在", status_code=404)
    return _questionnaire_response(questionnaire)


def create_admin_questionnaire(db: Session, request: AdminQuestionnaireCreateRequest) -> QuestionnaireResponse:
    existing = repository.get_questionnaire_by_code_version(db, code=request.code, version=request.version)
    if existing is not None:
        raise QuestionnaireServiceError("相同编码和版本的问卷已存在", status_code=409)

    questionnaire = repository.create_questionnaire(db, request)
    db.commit()
    detail = repository.get_questionnaire_detail(db, questionnaire.id)
    if detail is None:
        raise QuestionnaireServiceError("问卷创建后读取失败", status_code=500)
    return _questionnaire_response(detail)


def publish_admin_questionnaire(db: Session, questionnaire_id: int) -> QuestionnaireResponse:
    questionnaire = repository.get_questionnaire_detail(db, questionnaire_id)
    if questionnaire is None:
        raise QuestionnaireServiceError("问卷不存在", status_code=404)
    repository.publish_questionnaire(db, questionnaire)
    db.commit()
    db.refresh(questionnaire)
    detail = repository.get_questionnaire_detail(db, questionnaire_id)
    if detail is None:
        raise QuestionnaireServiceError("问卷发布后读取失败", status_code=500)
    return _questionnaire_response(detail)


def get_current_questionnaire(db: Session, *, code: str | None) -> QuestionnaireResponse:
    questionnaire = repository.get_current_published_questionnaire(db, code=code)
    if questionnaire is None:
        raise QuestionnaireServiceError("暂无已发布问卷", status_code=404)
    return _questionnaire_response(questionnaire)


def get_published_questionnaire(db: Session, questionnaire_id: int) -> QuestionnaireSet:
    questionnaire = repository.get_questionnaire_detail(db, questionnaire_id)
    if questionnaire is None or questionnaire.status != "published":
        raise QuestionnaireServiceError("问卷不存在或未发布", status_code=404)
    return questionnaire


def _score_json(score_json: dict[str, Any] | None) -> dict[str, int]:
    scores: dict[str, int] = {}
    for key, value in (score_json or {}).items():
        if isinstance(value, bool):
            continue
        if isinstance(value, int | float):
            scores[key] = int(value)
    return scores


def _rule_number(rule: dict[str, Any], *keys: str) -> int | None:
    for key in keys:
        value = rule.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int | float):
            return int(value)
    return None


def _check_min_max(value: int, rule: dict[str, Any], *, min_keys: tuple[str, ...], max_keys: tuple[str, ...]) -> bool:
    min_value = _rule_number(rule, *min_keys)
    max_value = _rule_number(rule, *max_keys)
    if min_value is not None and value < min_value:
        return False
    if max_value is not None and value > max_value:
        return False
    return True


def _profile_matches_rule(
    profile: QuestionnaireResultProfile,
    *,
    total_score: int,
    dimension_scores: dict[str, int],
    bias_counter: Counter[str],
) -> bool:
    rule = profile.rule_json or {}
    if not rule:
        return False

    if not _check_min_max(
        total_score,
        rule,
        min_keys=("min_total_score", "total_min", "min_score"),
        max_keys=("max_total_score", "total_max", "max_score"),
    ):
        return False

    dimension_code = rule.get("dimension_code")
    if isinstance(dimension_code, str):
        dimension_score = dimension_scores.get(dimension_code, 0)
        if not _check_min_max(
            dimension_score,
            rule,
            min_keys=("min_dimension_score", "dimension_min"),
            max_keys=("max_dimension_score", "dimension_max"),
        ):
            return False

    dimension_rules = rule.get("dimension_scores")
    if isinstance(dimension_rules, dict):
        for code, dimension_rule in dimension_rules.items():
            if isinstance(dimension_rule, dict):
                if not _check_min_max(
                    dimension_scores.get(code, 0),
                    dimension_rule,
                    min_keys=("min", "min_score"),
                    max_keys=("max", "max_score"),
                ):
                    return False
            elif isinstance(dimension_rule, int | float) and dimension_scores.get(code, 0) < int(dimension_rule):
                return False

    required_bias = rule.get("required_profile_bias") or rule.get("profile_bias")
    if isinstance(required_bias, str) and bias_counter.get(required_bias, 0) <= 0:
        return False

    return True


def _select_profile(
    profiles: list[QuestionnaireResultProfile],
    *,
    total_score: int,
    dimension_scores: dict[str, int],
    bias_counter: Counter[str],
) -> QuestionnaireResultProfile | None:
    for profile in sorted(profiles, key=lambda item: item.id):
        if _profile_matches_rule(
            profile,
            total_score=total_score,
            dimension_scores=dimension_scores,
            bias_counter=bias_counter,
        ):
            return profile

    for profile_code, _count in bias_counter.most_common():
        for profile in profiles:
            if profile.profile_code == profile_code:
                return profile

    return profiles[0] if profiles else None


def calculate_submission_result(
    questionnaire: QuestionnaireSet,
    request: QuestionnaireSubmitRequest,
) -> SubmissionCalculation:
    question_map = {question.id: question for question in questionnaire.questions if question.status == "active"}
    answers_by_question: dict[int, list[int]] = {}
    for answer in request.answers:
        if answer.question_id in answers_by_question:
            raise QuestionnaireServiceError("同一题目不能重复提交", status_code=400)
        answers_by_question[answer.question_id] = answer.option_ids

    missing_required = [
        question.id
        for question in question_map.values()
        if question.is_required and question.id not in answers_by_question
    ]
    if missing_required:
        raise QuestionnaireServiceError("存在未作答的必答题", status_code=400)

    total_score = 0
    dimension_scores: dict[str, int] = {}
    answers_snapshot: list[dict[str, Any]] = []
    answer_rows: list[dict[str, Any]] = []
    bias_counter: Counter[str] = Counter()

    for question_id, option_ids in answers_by_question.items():
        question = question_map.get(question_id)
        if question is None:
            raise QuestionnaireServiceError("题目不存在或已停用", status_code=400)
        if question.question_type == "single_choice" and len(option_ids) != 1:
            raise QuestionnaireServiceError("单选题只能选择一个选项", status_code=400)

        option_map: dict[int, QuestionnaireOption] = {option.id: option for option in question.options}
        selected_options: list[dict[str, Any]] = []
        for option_id in option_ids:
            option = option_map.get(option_id)
            if option is None:
                raise QuestionnaireServiceError("选项不存在或不属于当前题目", status_code=400)

            scores = _score_json(option.score_json)
            total_score += sum(scores.values())
            for dimension_code, score in scores.items():
                dimension_scores[dimension_code] = dimension_scores.get(dimension_code, 0) + score
            if option.profile_bias:
                bias_counter[option.profile_bias] += 1

            selected_options.append(
                {
                    "option_id": option.id,
                    "option_label": option.option_label,
                    "title": option.title,
                    "score_json": scores,
                    "profile_bias": option.profile_bias,
                }
            )
            answer_rows.append(
                {
                    "question_id": question.id,
                    "option_id": option.id,
                    "score_json": scores,
                }
            )

        answers_snapshot.append(
            {
                "question_id": question.id,
                "title": question.title,
                "dimension_code": question.dimension_code,
                "question_type": question.question_type,
                "selected_options": selected_options,
            }
        )

    profile = _select_profile(
        questionnaire.profiles,
        total_score=total_score,
        dimension_scores=dimension_scores,
        bias_counter=bias_counter,
    )
    result_response = _profile_response(profile) if profile else None
    return SubmissionCalculation(
        profile=profile,
        total_score=total_score,
        dimension_scores=dimension_scores,
        answers_snapshot=answers_snapshot,
        answer_rows=answer_rows,
        result_response=result_response,
    )


def _submission_response(submission: QuestionnaireSubmission) -> QuestionnaireSubmissionResponse:
    result_payload = submission.result_snapshot_json
    result = QuestionnaireProfileResponse(**result_payload) if result_payload else None
    return QuestionnaireSubmissionResponse(
        id=submission.id,
        questionnaire_id=submission.questionnaire_id,
        profile_code=submission.profile_code,
        profile_name=result.profile_name if result else None,
        total_score=submission.total_score,
        dimension_scores=submission.dimension_scores_json or {},
        result=result,
        answers_snapshot=submission.answers_snapshot_json or [],
    )


def submit_questionnaire(
    db: Session,
    *,
    questionnaire_id: int,
    user: AppUser,
    request: QuestionnaireSubmitRequest,
) -> QuestionnaireSubmissionResponse:
    questionnaire = get_published_questionnaire(db, questionnaire_id)
    calculation = calculate_submission_result(questionnaire, request)
    result_snapshot = calculation.result_response.model_dump() if calculation.result_response else None
    submission = repository.create_submission(
        db,
        user_id=user.id,
        enterprise_id=request.enterprise_id,
        lead_id=request.lead_id,
        questionnaire_id=questionnaire.id,
        result_profile_id=calculation.profile.id if calculation.profile else None,
        profile_code=calculation.profile.profile_code if calculation.profile else None,
        total_score=calculation.total_score,
        dimension_scores=calculation.dimension_scores,
        answers_snapshot=calculation.answers_snapshot,
        result_snapshot=result_snapshot,
        answer_rows=calculation.answer_rows,
    )
    db.commit()
    db.refresh(submission)
    return _submission_response(submission)


def get_submission_for_user(db: Session, *, submission_id: int, user: AppUser) -> QuestionnaireSubmissionResponse:
    submission = repository.get_submission_by_id(db, submission_id)
    if submission is None or submission.user_id != user.id:
        raise QuestionnaireServiceError("答题记录不存在", status_code=404)
    return _submission_response(submission)
