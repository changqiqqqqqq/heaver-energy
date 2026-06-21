"""供应商和转接记录模型。"""

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.common.datetime import utc_now
from app.db.base import Base

IdType = BigInteger().with_variant(Integer, "sqlite")


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    supplier_type: Mapped[str] = mapped_column(String(32), nullable=False)
    region_scope_json: Mapped[list[str] | None] = mapped_column(JSON)
    service_tags_json: Mapped[list[str] | None] = mapped_column(JSON)
    contact_name: Mapped[str | None] = mapped_column(String(64))
    contact_phone_masked: Mapped[str | None] = mapped_column(String(32))
    contact_phone_cipher: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    remark: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (Index("idx_suppliers_type_status", "supplier_type", "status"),)


class SupplierTransfer(Base):
    __tablename__ = "supplier_transfers"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    service_request_id: Mapped[int | None] = mapped_column(ForeignKey("service_requests.id"))
    transfer_status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    transfer_reason: Mapped[str | None] = mapped_column(String(512))
    operator_admin_id: Mapped[int] = mapped_column(IdType, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    __table_args__ = (
        Index("idx_supplier_transfers_lead", "lead_id", "created_at"),
        Index("idx_supplier_transfers_supplier", "supplier_id", "transfer_status"),
    )

