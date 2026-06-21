"""统计模块数据访问。"""

from datetime import datetime

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.modules.enterprise.model import Enterprise
from app.modules.lead.model import Lead
from app.modules.questionnaire.model import QuestionnaireSubmission
from app.modules.screening.model import ScreeningRequest
from app.modules.service_request.model import ServiceRequest


def count_leads(db: Session) -> int:
    return int(db.scalar(select(func.count()).select_from(Lead).where(Lead.deleted_at.is_(None))) or 0)


def count_leads_since(db: Session, since: datetime) -> int:
    return int(db.scalar(select(func.count()).select_from(Lead).where(Lead.deleted_at.is_(None), Lead.created_at >= since)) or 0)


def count_leads_by_grade(db: Session) -> dict[str, int]:
    rows = db.execute(
        select(Lead.lead_grade, func.count()).where(Lead.deleted_at.is_(None)).group_by(Lead.lead_grade)
    ).all()
    return {str(grade or "unknown"): int(count) for grade, count in rows}


def count_by_status(db: Session, status: str) -> int:
    return int(db.scalar(select(func.count()).select_from(Lead).where(Lead.deleted_at.is_(None), Lead.lead_status == status)) or 0)


def count_bill_uploaded(db: Session) -> int:
    return int(db.scalar(select(func.count()).select_from(Lead).where(Lead.deleted_at.is_(None), Lead.has_bill_uploaded.is_(True))) or 0)


def count_phone_authorized(db: Session) -> int:
    return int(db.scalar(select(func.count()).select_from(Lead).where(Lead.deleted_at.is_(None), Lead.has_phone_authorized.is_(True))) or 0)


def count_leads_between(db: Session, start_at: datetime, end_at: datetime) -> int:
    return int(
        db.scalar(
            select(func.count())
            .select_from(Lead)
            .where(Lead.deleted_at.is_(None), Lead.created_at >= start_at, Lead.created_at < end_at)
        )
        or 0
    )


def count_submissions_between(db: Session, start_at: datetime, end_at: datetime) -> int:
    return int(
        db.scalar(
            select(func.count())
            .select_from(QuestionnaireSubmission)
            .where(QuestionnaireSubmission.created_at >= start_at, QuestionnaireSubmission.created_at < end_at)
        )
        or 0
    )


def count_screenings_between(db: Session, start_at: datetime, end_at: datetime) -> int:
    return int(
        db.scalar(
            select(func.count())
            .select_from(ScreeningRequest)
            .where(ScreeningRequest.submitted_at >= start_at, ScreeningRequest.submitted_at < end_at)
        )
        or 0
    )


def count_service_requests_between(db: Session, start_at: datetime, end_at: datetime) -> int:
    return int(
        db.scalar(
            select(func.count())
            .select_from(ServiceRequest)
            .where(
                ServiceRequest.deleted_at.is_(None),
                ServiceRequest.submitted_at >= start_at,
                ServiceRequest.submitted_at < end_at,
            )
        )
        or 0
    )


def _daily_counts(db: Session, column, model, start_at: datetime, end_at: datetime, *conditions) -> dict[str, int]:
    day_label = func.date(column).label("day")
    rows = db.execute(
        select(day_label, func.count())
        .select_from(model)
        .where(column >= start_at, column < end_at, *conditions)
        .group_by(day_label)
    ).all()
    return {str(day): int(count) for day, count in rows}


def count_leads_by_day(db: Session, start_at: datetime, end_at: datetime) -> dict[str, int]:
    return _daily_counts(db, Lead.created_at, Lead, start_at, end_at, Lead.deleted_at.is_(None))


def count_submissions_by_day(db: Session, start_at: datetime, end_at: datetime) -> dict[str, int]:
    return _daily_counts(db, QuestionnaireSubmission.created_at, QuestionnaireSubmission, start_at, end_at)


def count_screenings_by_day(db: Session, start_at: datetime, end_at: datetime) -> dict[str, int]:
    return _daily_counts(db, ScreeningRequest.submitted_at, ScreeningRequest, start_at, end_at)


def count_service_requests_by_day(db: Session, start_at: datetime, end_at: datetime) -> dict[str, int]:
    return _daily_counts(
        db,
        ServiceRequest.submitted_at,
        ServiceRequest,
        start_at,
        end_at,
        ServiceRequest.deleted_at.is_(None),
    )


def count_profiles_between(db: Session, start_at: datetime, end_at: datetime) -> dict[str, int]:
    rows = db.execute(
        select(QuestionnaireSubmission.profile_code, func.count())
        .where(
            QuestionnaireSubmission.created_at >= start_at,
            QuestionnaireSubmission.created_at < end_at,
            QuestionnaireSubmission.profile_code.is_not(None),
        )
        .group_by(QuestionnaireSubmission.profile_code)
    ).all()
    return {str(profile_code): int(count) for profile_code, count in rows if profile_code}


def count_consultations_by_profile_between(db: Session, start_at: datetime, end_at: datetime) -> dict[str, int]:
    rows = db.execute(
        select(QuestionnaireSubmission.profile_code, func.count(func.distinct(ServiceRequest.lead_id)))
        .select_from(ServiceRequest)
        .join(
            QuestionnaireSubmission,
            QuestionnaireSubmission.lead_id == ServiceRequest.lead_id,
        )
        .where(
            ServiceRequest.deleted_at.is_(None),
            ServiceRequest.submitted_at >= start_at,
            ServiceRequest.submitted_at < end_at,
            ServiceRequest.lead_id.is_not(None),
            QuestionnaireSubmission.profile_code.is_not(None),
        )
        .group_by(QuestionnaireSubmission.profile_code)
    ).all()
    return {str(profile_code): int(count) for profile_code, count in rows if profile_code}


def list_pending_message_leads(db: Session, limit: int) -> list[tuple[Lead, str | None]]:
    return list(
        db.execute(
            select(Lead, Enterprise.name)
            .outerjoin(Enterprise, Enterprise.id == Lead.enterprise_id)
            .where(Lead.deleted_at.is_(None), Lead.lead_status == "pending_followup")
            .order_by(desc(Lead.last_activity_at), desc(Lead.created_at))
            .limit(limit)
        ).all()
    )

