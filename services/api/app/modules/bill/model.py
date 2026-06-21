"""账单上传与结构化电费账单模型。"""

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.common.datetime import utc_now
from app.db.base import Base

IdType = BigInteger().with_variant(Integer, "sqlite")


class BillUpload(Base):
    __tablename__ = "bill_uploads"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    enterprise_id: Mapped[int | None] = mapped_column(ForeignKey("enterprises.id"))
    lead_id: Mapped[int | None] = mapped_column(ForeignKey("leads.id"))
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id"), nullable=False)
    bill_month: Mapped[str | None] = mapped_column(String(16))
    upload_source: Mapped[str] = mapped_column(String(32), default="miniapp", nullable=False)
    parse_status: Mapped[str] = mapped_column(String(32), default="not_parsed", nullable=False)
    parsed_result_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    manual_remark: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_bill_uploads_enterprise", "enterprise_id", "created_at"),
        Index("idx_bill_uploads_lead", "lead_id"),
        Index("idx_bill_uploads_parse_status", "parse_status"),
    )


class ElectricityBill(Base):
    __tablename__ = "electricity_bills"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    enterprise_id: Mapped[int] = mapped_column(ForeignKey("enterprises.id"), nullable=False)
    bill_upload_id: Mapped[int | None] = mapped_column(ForeignKey("bill_uploads.id"))
    bill_month: Mapped[str] = mapped_column(String(16), nullable=False)
    total_kwh: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    total_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    peak_kwh: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    flat_kwh: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    valley_kwh: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    capacity_fee: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    demand_fee: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    raw_data_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("uk_electricity_bill_month", "enterprise_id", "bill_month", unique=True),
        Index("idx_electricity_bills_month", "bill_month"),
    )

