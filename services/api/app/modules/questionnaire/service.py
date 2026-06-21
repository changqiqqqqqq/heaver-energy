"""测评题库、评分与答题业务服务。"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.common.enums import PROFILE_CODES, PROFILE_PRIORITY, SCORE_DIMENSIONS
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
    QuestionnaireResultPageResponse,
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
    lead_grade: str
    total_score: int
    dimension_scores: dict[str, int]
    dimension_stars: dict[str, int]
    answer_tags: dict[str, Any]
    answers_snapshot: list[dict[str, Any]]
    answer_rows: list[dict[str, Any]]
    result_response: QuestionnaireProfileResponse | None


def _result_page_response(profile: QuestionnaireResultProfile) -> QuestionnaireResultPageResponse | None:
    if not profile.result_page_json:
        return None
    return QuestionnaireResultPageResponse(**profile.result_page_json)


def _profile_response(profile: QuestionnaireResultProfile) -> QuestionnaireProfileResponse:
    return QuestionnaireProfileResponse(
        profile_code=profile.profile_code,
        profile_name=profile.profile_name,
        lead_grade_suggestion=profile.lead_grade_suggestion,
        theme_color=profile.theme_color,
        tags=profile.tags_json or [],
        summary=profile.summary,
        recommendations=profile.recommendations_json or [],
        result_page=_result_page_response(profile),
    )


def _question_response(question: QuestionnaireQuestion) -> QuestionnaireQuestionResponse:
    active_options = sorted(question.options, key=lambda option: option.sort_order)
    return QuestionnaireQuestionResponse(
        id=question.id,
        question_code=question.question_code,
        title=question.title,
        subtitle=question.subtitle,
        dimension_code=question.dimension_code,
        question_type=question.question_type,
        score_mode=question.score_mode,
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
        profiles=[_profile_response(profile) for profile in sorted(questionnaire.profiles, key=lambda item: item.priority)],
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
        if key not in SCORE_DIMENSIONS:
            raise QuestionnaireServiceError(f"不支持的评分维度：{key}", status_code=400)
        if isinstance(value, bool):
            continue
        if isinstance(value, int | float):
            scores[key] = int(value)
    return scores


def score_to_star(score: int) -> int:
    if score <= 2:
        return 1
    if score <= 5:
        return 2
    if score <= 8:
        return 3
    if score <= 11:
        return 4
    return 5


def _dimension_stars(dimension_scores: dict[str, int]) -> dict[str, int]:
    return {dimension: score_to_star(dimension_scores.get(dimension, 0)) for dimension in SCORE_DIMENSIONS}


def _merge_answer_tags(answer_tags: dict[str, Any], tags: dict[str, Any] | None) -> None:
    for key, value in (tags or {}).items():
        if value is None:
            continue
        if isinstance(value, list):
            current = answer_tags.setdefault(key, [])
            if isinstance(current, list):
                current.extend(item for item in value if item not in current)
            else:
                answer_tags[key] = value
        elif key not in answer_tags:
            answer_tags[key] = value
        elif answer_tags[key] != value:
            current = answer_tags[key]
            if isinstance(current, list):
                if value not in current:
                    current.append(value)
            else:
                answer_tags[key] = [current, value]


def _is_highest(dimension_scores: dict[str, int], dimension: str) -> bool:
    focus_dimensions = ("CP", "MA", "SR", "EP")
    value = dimension_scores.get(dimension, 0)
    return value > 0 and value >= max(dimension_scores.get(item, 0) for item in focus_dimensions)


def _target_profile_code(dimension_scores: dict[str, int], answer_tags: dict[str, Any]) -> str:
    cp = dimension_scores.get("CP", 0)
    ma = dimension_scores.get("MA", 0)
    sr = dimension_scores.get("SR", 0)
    ep = dimension_scores.get("EP", 0)
    lv = dimension_scores.get("LV", 0)
    profile_tags = answer_tags.get("profile_tags") or []

    if ma >= 5 and (_is_highest(dimension_scores, "MA") or cp >= 3):
        return "hidden_waste"
    if ep >= 5 and _is_highest(dimension_scores, "EP"):
        return "energy_awakened"
    if sr >= 6 and _is_highest(dimension_scores, "SR"):
        return "supplier_confused"
    if cp >= 6:
        return "cost_sensitive"
    if (ma >= 3 and lv >= 3) or "growth_expansion" in profile_tags:
        return "growth_expansion"
    return "stable_operation"


def _select_profile(
    profiles: list[QuestionnaireResultProfile],
    *,
    dimension_scores: dict[str, int],
    answer_tags: dict[str, Any],
    bias_counter: Counter[str],
) -> QuestionnaireResultProfile | None:
    if not profiles:
        return None

    target_code = _target_profile_code(dimension_scores, answer_tags)
    profile_map = {profile.profile_code: profile for profile in profiles}
    if target_code in profile_map:
        return profile_map[target_code]

    for profile_code, _count in bias_counter.most_common():
        if profile_code in profile_map:
            return profile_map[profile_code]

    return sorted(
        profiles,
        key=lambda item: (PROFILE_PRIORITY.get(item.profile_code, item.priority), item.priority, item.id),
    )[0]


def _lead_grade(dimension_scores: dict[str, int]) -> str:
    am = dimension_scores.get("AM", 0)
    lv = dimension_scores.get("LV", 0)
    if am >= 8 and lv >= 4:
        return "A"
    if am >= 5 or lv >= 3:
        return "B"
    if am >= 2:
        return "C"
    return "D"


def _primary_need_type(dimension_scores: dict[str, int], answer_tags: dict[str, Any]) -> str | None:
    need_types = answer_tags.get("need_types")
    if isinstance(need_types, list) and need_types:
        return str(need_types[0])
    if dimension_scores.get("EP", 0) >= 5:
        return "use_energy"
    if dimension_scores.get("SR", 0) >= 6:
        return "quote_review"
    return None


def _need_tags(answer_tags: dict[str, Any]) -> list[str]:
    tags = answer_tags.get("need_tags")
    if isinstance(tags, list):
        return [str(item) for item in tags]
    if isinstance(tags, str):
        return [tags]
    return []


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
    dimension_scores: dict[str, int] = {dimension: 0 for dimension in SCORE_DIMENSIONS}
    answer_tags: dict[str, Any] = {}
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
        question_snapshot = {
            "question_id": question.id,
            "question_code": question.question_code,
            "title": question.title,
            "score_mode": question.score_mode,
            "question_type": question.question_type,
        }
        for option_id in option_ids:
            option = option_map.get(option_id)
            if option is None:
                raise QuestionnaireServiceError("选项不存在或不属于当前题目", status_code=400)

            scores = {} if question.score_mode == "tag_only" else _score_json(option.score_json)
            total_score += sum(scores.values())
            for dimension_code, score in scores.items():
                dimension_scores[dimension_code] = dimension_scores.get(dimension_code, 0) + score
            _merge_answer_tags(answer_tags, option.tags_json)
            if option.profile_bias:
                bias_counter[option.profile_bias] += 1

            option_snapshot = {
                "option_id": option.id,
                "option_label": option.option_label,
                "title": option.title,
                "score_json": scores,
                "tags_json": option.tags_json or {},
                "profile_bias": option.profile_bias,
            }
            selected_options.append(option_snapshot)
            answer_rows.append(
                {
                    "question_id": question.id,
                    "option_id": option.id,
                    "question_snapshot": question_snapshot,
                    "option_snapshot": option_snapshot,
                    "score_json": scores,
                    "tags_json": option.tags_json or {},
                }
            )

        answers_snapshot.append({**question_snapshot, "selected_options": selected_options})

    profile = _select_profile(
        questionnaire.profiles,
        dimension_scores=dimension_scores,
        answer_tags=answer_tags,
        bias_counter=bias_counter,
    )
    result_response = _profile_response(profile) if profile else None
    dimension_stars = _dimension_stars(dimension_scores)
    return SubmissionCalculation(
        profile=profile,
        lead_grade=_lead_grade(dimension_scores),
        total_score=total_score,
        dimension_scores=dimension_scores,
        dimension_stars=dimension_stars,
        answer_tags=answer_tags,
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
        lead_id=submission.lead_id,
        profile_code=submission.profile_code,
        profile_name=result.profile_name if result else None,
        lead_grade=submission.lead_grade,
        total_score=submission.total_score,
        dimension_scores=submission.dimension_scores_json or {},
        dimension_stars=submission.dimension_stars_json or {},
        answer_tags=submission.answer_tags_json or {},
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

    from app.modules.lead.schema import LeadInternalUpsert
    from app.modules.lead.service import create_or_update_lead

    lead = create_or_update_lead(
        db,
        LeadInternalUpsert(
            user_id=user.id,
            enterprise_id=request.enterprise_id,
            lead_id=request.lead_id,
            source_entry="questionnaire",
            lead_grade=calculation.lead_grade,
            primary_need_type=_primary_need_type(calculation.dimension_scores, calculation.answer_tags),
            profile_code=calculation.profile.profile_code if calculation.profile else None,
            score_snapshot={
                "dimension_scores": calculation.dimension_scores,
                "dimension_stars": calculation.dimension_stars,
                "answer_tags": calculation.answer_tags,
            },
            need_tags=_need_tags(calculation.answer_tags),
            result_summary=calculation.result_response.summary if calculation.result_response else None,
            has_phone_authorized=bool(user.phone_hash),
        ),
    )

    submission = repository.create_submission(
        db,
        user_id=user.id,
        enterprise_id=request.enterprise_id or lead.enterprise_id,
        lead_id=lead.id,
        questionnaire_id=questionnaire.id,
        result_profile_id=calculation.profile.id if calculation.profile else None,
        profile_code=calculation.profile.profile_code if calculation.profile else None,
        lead_grade=calculation.lead_grade,
        total_score=calculation.total_score,
        dimension_scores=calculation.dimension_scores,
        dimension_stars=calculation.dimension_stars,
        answer_tags=calculation.answer_tags,
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
