"""免费初筛数据访问。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.screening.model import ScreeningRequest


def add_screening(db: Session, screening: ScreeningRequest) -> ScreeningRequest:
    db.add(screening)
    db.flush()
    return screening


def list_screenings_by_lead(db: Session, lead_id: int) -> list[ScreeningRequest]:
    statement = (
        select(ScreeningRequest)
        .where(ScreeningRequest.lead_id == lead_id)
        .order_by(ScreeningRequest.submitted_at.desc())
    )
    return list(db.scalars(statement).all())

