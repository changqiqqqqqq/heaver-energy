"""账单数据访问。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.bill.model import BillUpload


def add_bill_upload(db: Session, bill_upload: BillUpload) -> BillUpload:
    db.add(bill_upload)
    db.flush()
    return bill_upload


def list_bill_uploads_by_lead(db: Session, lead_id: int) -> list[BillUpload]:
    statement = (
        select(BillUpload)
        .where(BillUpload.lead_id == lead_id, BillUpload.deleted_at.is_(None))
        .order_by(BillUpload.created_at.desc())
    )
    return list(db.scalars(statement).all())

