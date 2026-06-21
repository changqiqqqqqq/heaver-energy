"""CRM 数据访问。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.crm.model import LeadFollowup, LeadNote


def add_followup(db: Session, followup: LeadFollowup) -> LeadFollowup:
    db.add(followup)
    db.flush()
    return followup


def add_note(db: Session, note: LeadNote) -> LeadNote:
    db.add(note)
    db.flush()
    return note


def list_followups_by_lead(db: Session, lead_id: int) -> list[LeadFollowup]:
    statement = select(LeadFollowup).where(LeadFollowup.lead_id == lead_id).order_by(LeadFollowup.created_at.desc())
    return list(db.scalars(statement).all())


def list_notes_by_lead(db: Session, lead_id: int) -> list[LeadNote]:
    statement = (
        select(LeadNote)
        .where(LeadNote.lead_id == lead_id, LeadNote.deleted_at.is_(None))
        .order_by(LeadNote.created_at.desc())
    )
    return list(db.scalars(statement).all())

