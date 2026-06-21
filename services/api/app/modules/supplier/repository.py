"""供应商数据访问。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.supplier.model import Supplier, SupplierTransfer


def add_supplier(db: Session, supplier: Supplier) -> Supplier:
    db.add(supplier)
    db.flush()
    return supplier


def get_supplier_by_id(db: Session, supplier_id: int) -> Supplier | None:
    statement = select(Supplier).where(Supplier.id == supplier_id, Supplier.deleted_at.is_(None))
    return db.scalar(statement)


def list_suppliers(db: Session) -> list[Supplier]:
    statement = select(Supplier).where(Supplier.deleted_at.is_(None)).order_by(Supplier.id.desc())
    return list(db.scalars(statement).all())


def add_transfer(db: Session, transfer: SupplierTransfer) -> SupplierTransfer:
    db.add(transfer)
    db.flush()
    return transfer


def list_transfers_by_lead(db: Session, lead_id: int) -> list[SupplierTransfer]:
    statement = select(SupplierTransfer).where(SupplierTransfer.lead_id == lead_id).order_by(SupplierTransfer.created_at.desc())
    return list(db.scalars(statement).all())

