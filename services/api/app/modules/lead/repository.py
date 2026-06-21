"""线索模块数据访问。"""

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.modules.enterprise.model import Enterprise
from app.modules.lead.model import Lead, LeadStatusLog


def _lead_base_statement() -> Select:
    return select(Lead, Enterprise.name).outerjoin(Enterprise, Lead.enterprise_id == Enterprise.id).where(
        Lead.deleted_at.is_(None)
    )


def get_lead_by_id(db: Session, lead_id: int) -> Lead | None:
    statement = select(Lead).where(Lead.id == lead_id, Lead.deleted_at.is_(None))
    return db.scalar(statement)


def get_latest_open_lead(db: Session, *, user_id: int | None, enterprise_id: int | None = None) -> Lead | None:
    conditions = [Lead.deleted_at.is_(None), Lead.lead_status != "closed"]
    if enterprise_id is not None:
        conditions.append(Lead.enterprise_id == enterprise_id)
    elif user_id is not None:
        conditions.append(Lead.user_id == user_id)
    else:
        return None
    statement = select(Lead).where(*conditions).order_by(Lead.last_activity_at.desc(), Lead.id.desc()).limit(1)
    return db.scalar(statement)


def add_lead(db: Session, lead: Lead) -> Lead:
    db.add(lead)
    db.flush()
    return lead


def add_status_log(db: Session, status_log: LeadStatusLog) -> LeadStatusLog:
    db.add(status_log)
    db.flush()
    return status_log


def list_leads(
    db: Session,
    *,
    page: int,
    page_size: int,
    lead_grade: str | None = None,
    lead_status: str | None = None,
    profile_code: str | None = None,
    primary_need_type: str | None = None,
    has_bill_uploaded: bool | None = None,
    has_phone_authorized: bool | None = None,
) -> tuple[list[tuple[Lead, str | None]], int]:
    statement = _lead_base_statement()
    count_statement = select(func.count()).select_from(Lead).where(Lead.deleted_at.is_(None))
    filters = []
    if lead_grade:
        filters.append(Lead.lead_grade == lead_grade)
    if lead_status:
        filters.append(Lead.lead_status == lead_status)
    if profile_code:
        filters.append(Lead.profile_code == profile_code)
    if primary_need_type:
        filters.append(Lead.primary_need_type == primary_need_type)
    if has_bill_uploaded is not None:
        filters.append(Lead.has_bill_uploaded.is_(has_bill_uploaded))
    if has_phone_authorized is not None:
        filters.append(Lead.has_phone_authorized.is_(has_phone_authorized))
    if filters:
        statement = statement.where(*filters)
        count_statement = count_statement.where(*filters)

    total = int(db.scalar(count_statement) or 0)
    rows = db.execute(
        statement.order_by(Lead.last_activity_at.desc(), Lead.id.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return [(row[0], row[1]) for row in rows], total


def get_lead_with_enterprise_name(db: Session, lead_id: int) -> tuple[Lead, str | None] | None:
    row = db.execute(_lead_base_statement().where(Lead.id == lead_id)).first()
    if row is None:
        return None
    return row[0], row[1]

