"""企业模块数据访问。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.enterprise.model import Enterprise, EnterpriseContact


def get_enterprise_by_id(db: Session, enterprise_id: int) -> Enterprise | None:
    statement = select(Enterprise).where(Enterprise.id == enterprise_id, Enterprise.deleted_at.is_(None))
    return db.scalar(statement)


def get_primary_contact(db: Session, enterprise_id: int) -> EnterpriseContact | None:
    statement = (
        select(EnterpriseContact)
        .where(
            EnterpriseContact.enterprise_id == enterprise_id,
            EnterpriseContact.is_primary.is_(True),
            EnterpriseContact.deleted_at.is_(None),
        )
        .order_by(EnterpriseContact.id.asc())
        .limit(1)
    )
    return db.scalar(statement)


def get_contact_by_phone_hash(db: Session, phone_hash: str) -> EnterpriseContact | None:
    statement = select(EnterpriseContact).where(
        EnterpriseContact.phone_hash == phone_hash,
        EnterpriseContact.deleted_at.is_(None),
    )
    return db.scalar(statement)


def add_enterprise(db: Session, enterprise: Enterprise) -> Enterprise:
    db.add(enterprise)
    db.flush()
    return enterprise


def add_contact(db: Session, contact: EnterpriseContact) -> EnterpriseContact:
    db.add(contact)
    db.flush()
    return contact

