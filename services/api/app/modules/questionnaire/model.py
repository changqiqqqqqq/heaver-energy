"""经营体质测评题库、画像与答题记录模型。"""

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.datetime import utc_now
from app.db.base import Base

IdType = BigInteger().with_variant(Integer, "sqlite")


class QuestionnaireSet(Base):
    __tablename__ = "questionnaire_sets"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    version: Mapped[str] = mapped_column(String(32), default="v1", nullable=False)
    description: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)
    result_config_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    questions: Mapped[list["QuestionnaireQuestion"]] = relationship(
        back_populates="questionnaire",
        cascade="all, delete-orphan",
        order_by="QuestionnaireQuestion.sort_order",
    )
    profiles: Mapped[list["QuestionnaireResultProfile"]] = relationship(
        back_populates="questionnaire",
        cascade="all, delete-orphan",
    )

    __table_args__ = (Index("uk_questionnaire_code_version", "code", "version", unique=True),)


class QuestionnaireQuestion(Base):
    __tablename__ = "questionnaire_questions"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    questionnaire_id: Mapped[int] = mapped_column(ForeignKey("questionnaire_sets.id"), nullable=False)
    question_code: Mapped[str | None] = mapped_column(String(32))
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    subtitle: Mapped[str | None] = mapped_column(String(256))
    dimension_code: Mapped[str | None] = mapped_column(String(64))
    question_type: Mapped[str] = mapped_column(String(32), default="single_choice", nullable=False)
    score_mode: Mapped[str] = mapped_column(String(32), default="score", nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_required: Mapped[bool] = mapped_column(default=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    questionnaire: Mapped[QuestionnaireSet] = relationship(back_populates="questions")
    options: Mapped[list["QuestionnaireOption"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuestionnaireOption.sort_order",
    )

    __table_args__ = (
        Index("idx_questions_questionnaire_sort", "questionnaire_id", "sort_order"),
        Index("uk_questions_questionnaire_code", "questionnaire_id", "question_code", unique=True),
    )


class QuestionnaireOption(Base):
    __tablename__ = "questionnaire_options"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questionnaire_questions.id"), nullable=False)
    option_label: Mapped[str | None] = mapped_column(String(8))
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    subtitle: Mapped[str | None] = mapped_column(String(256))
    score_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    tags_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    profile_bias: Mapped[str | None] = mapped_column(String(64))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    question: Mapped[QuestionnaireQuestion] = relationship(back_populates="options")

    __table_args__ = (Index("idx_options_question_sort", "question_id", "sort_order"),)


class QuestionnaireResultProfile(Base):
    __tablename__ = "questionnaire_result_profiles"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    questionnaire_id: Mapped[int] = mapped_column(ForeignKey("questionnaire_sets.id"), nullable=False)
    profile_code: Mapped[str] = mapped_column(String(64), nullable=False)
    profile_name: Mapped[str] = mapped_column(String(64), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    lead_grade_suggestion: Mapped[str | None] = mapped_column(String(16))
    theme_color: Mapped[str | None] = mapped_column(String(32))
    tags_json: Mapped[list[str] | None] = mapped_column(JSON)
    summary: Mapped[str | None] = mapped_column(String(512))
    recommendations_json: Mapped[list[str] | None] = mapped_column(JSON)
    rule_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    result_page_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    questionnaire: Mapped[QuestionnaireSet] = relationship(back_populates="profiles")

    __table_args__ = (
        Index("uk_profile_questionnaire_code", "questionnaire_id", "profile_code", unique=True),
        Index("idx_profile_questionnaire_priority", "questionnaire_id", "priority"),
    )


class QuestionnaireSubmission(Base):
    __tablename__ = "questionnaire_submissions"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(IdType, nullable=False)
    enterprise_id: Mapped[int | None] = mapped_column(IdType)
    lead_id: Mapped[int | None] = mapped_column(IdType)
    questionnaire_id: Mapped[int] = mapped_column(ForeignKey("questionnaire_sets.id"), nullable=False)
    result_profile_id: Mapped[int | None] = mapped_column(ForeignKey("questionnaire_result_profiles.id"))
    profile_code: Mapped[str | None] = mapped_column(String(64))
    lead_grade: Mapped[str | None] = mapped_column(String(16))
    total_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dimension_scores_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    dimension_stars_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    answer_tags_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    answers_snapshot_json: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON)
    result_snapshot_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    answers: Mapped[list["QuestionnaireAnswer"]] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_submissions_user", "user_id", "created_at"),
        Index("idx_submissions_lead", "lead_id"),
        Index("idx_submissions_profile", "profile_code"),
        Index("idx_submissions_grade", "lead_grade", "created_at"),
    )


class QuestionnaireAnswer(Base):
    __tablename__ = "questionnaire_answers"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("questionnaire_submissions.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questionnaire_questions.id"), nullable=False)
    option_id: Mapped[int] = mapped_column(ForeignKey("questionnaire_options.id"), nullable=False)
    question_snapshot_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    option_snapshot_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    score_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    tags_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    submission: Mapped[QuestionnaireSubmission] = relationship(back_populates="answers")

    __table_args__ = (Index("idx_answers_submission", "submission_id"),)
