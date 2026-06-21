"""测评模块数据访问。"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.common.datetime import utc_now
from app.modules.questionnaire.model import (
    QuestionnaireAnswer,
    QuestionnaireOption,
    QuestionnaireQuestion,
    QuestionnaireResultProfile,
    QuestionnaireSet,
    QuestionnaireSubmission,
)
from app.modules.questionnaire.schema import AdminQuestionnaireCreateRequest


def list_questionnaires(db: Session) -> list[QuestionnaireSet]:
    statement = select(QuestionnaireSet).where(QuestionnaireSet.deleted_at.is_(None)).order_by(QuestionnaireSet.id.desc())
    return list(db.scalars(statement).all())


def get_questionnaire_by_code_version(db: Session, *, code: str, version: str) -> QuestionnaireSet | None:
    statement = select(QuestionnaireSet).where(
        QuestionnaireSet.code == code,
        QuestionnaireSet.version == version,
        QuestionnaireSet.deleted_at.is_(None),
    )
    return db.scalar(statement)


def get_current_published_questionnaire(db: Session, *, code: str | None = None) -> QuestionnaireSet | None:
    statement = (
        select(QuestionnaireSet)
        .options(
            selectinload(QuestionnaireSet.questions).selectinload(QuestionnaireQuestion.options),
            selectinload(QuestionnaireSet.profiles),
        )
        .where(
            QuestionnaireSet.status == "published",
            QuestionnaireSet.deleted_at.is_(None),
        )
        .order_by(QuestionnaireSet.published_at.desc(), QuestionnaireSet.id.desc())
        .limit(1)
    )
    if code:
        statement = statement.where(QuestionnaireSet.code == code)
    return db.scalar(statement)


def get_questionnaire_detail(db: Session, questionnaire_id: int) -> QuestionnaireSet | None:
    statement = (
        select(QuestionnaireSet)
        .options(
            selectinload(QuestionnaireSet.questions).selectinload(QuestionnaireQuestion.options),
            selectinload(QuestionnaireSet.profiles),
        )
        .where(QuestionnaireSet.id == questionnaire_id, QuestionnaireSet.deleted_at.is_(None))
    )
    return db.scalar(statement)


def create_questionnaire(db: Session, request: AdminQuestionnaireCreateRequest) -> QuestionnaireSet:
    questionnaire = QuestionnaireSet(
        code=request.code,
        name=request.name,
        version=request.version,
        description=request.description,
        status=request.status,
        result_config_json=request.result_config_json,
        published_at=utc_now() if request.status == "published" else None,
    )
    db.add(questionnaire)
    db.flush()

    for question_input in request.questions:
        question = QuestionnaireQuestion(
            questionnaire_id=questionnaire.id,
            question_code=question_input.question_code,
            title=question_input.title,
            subtitle=question_input.subtitle,
            dimension_code=question_input.dimension_code,
            question_type=question_input.question_type,
            score_mode=question_input.score_mode,
            sort_order=question_input.sort_order,
            is_required=question_input.is_required,
            status="active",
        )
        db.add(question)
        db.flush()

        for option_input in question_input.options:
            db.add(
                QuestionnaireOption(
                    question_id=question.id,
                    option_label=option_input.option_label,
                    title=option_input.title,
                    subtitle=option_input.subtitle,
                    score_json=option_input.score_json,
                    tags_json=option_input.tags_json,
                    profile_bias=option_input.profile_bias,
                    sort_order=option_input.sort_order,
                )
            )

    for profile_input in request.profiles:
        db.add(
            QuestionnaireResultProfile(
                questionnaire_id=questionnaire.id,
                profile_code=profile_input.profile_code,
                profile_name=profile_input.profile_name,
                priority=profile_input.priority,
                lead_grade_suggestion=profile_input.lead_grade_suggestion,
                theme_color=profile_input.theme_color,
                tags_json=profile_input.tags,
                summary=profile_input.summary,
                recommendations_json=profile_input.recommendations,
                rule_json=profile_input.rule_json,
                result_page_json=profile_input.result_page_json,
            )
        )

    db.flush()
    return questionnaire


def publish_questionnaire(db: Session, questionnaire: QuestionnaireSet) -> QuestionnaireSet:
    questionnaire.status = "published"
    questionnaire.published_at = utc_now()
    db.add(questionnaire)
    db.flush()
    return questionnaire


def create_submission(
    db: Session,
    *,
    user_id: int,
    enterprise_id: int | None,
    lead_id: int | None,
    questionnaire_id: int,
    result_profile_id: int | None,
    profile_code: str | None,
    lead_grade: str | None,
    total_score: int,
    dimension_scores: dict[str, int],
    dimension_stars: dict[str, int],
    answer_tags: dict[str, Any],
    answers_snapshot: list[dict[str, Any]],
    result_snapshot: dict[str, Any] | None,
    answer_rows: list[dict[str, Any]],
) -> QuestionnaireSubmission:
    submission = QuestionnaireSubmission(
        user_id=user_id,
        enterprise_id=enterprise_id,
        lead_id=lead_id,
        questionnaire_id=questionnaire_id,
        result_profile_id=result_profile_id,
        profile_code=profile_code,
        lead_grade=lead_grade,
        total_score=total_score,
        dimension_scores_json=dimension_scores,
        dimension_stars_json=dimension_stars,
        answer_tags_json=answer_tags,
        answers_snapshot_json=answers_snapshot,
        result_snapshot_json=result_snapshot,
    )
    db.add(submission)
    db.flush()

    for row in answer_rows:
        db.add(
            QuestionnaireAnswer(
                submission_id=submission.id,
                question_id=row["question_id"],
                option_id=row["option_id"],
                question_snapshot_json=row.get("question_snapshot"),
                option_snapshot_json=row.get("option_snapshot"),
                score_json=row.get("score_json"),
                tags_json=row.get("tags_json"),
            )
        )
    db.flush()
    return submission


def get_submission_by_id(db: Session, submission_id: int) -> QuestionnaireSubmission | None:
    return db.get(QuestionnaireSubmission, submission_id)


def list_submissions_by_lead(db: Session, lead_id: int) -> list[QuestionnaireSubmission]:
    statement = (
        select(QuestionnaireSubmission)
        .where(QuestionnaireSubmission.lead_id == lead_id)
        .order_by(QuestionnaireSubmission.created_at.desc())
    )
    return list(db.scalars(statement).all())
