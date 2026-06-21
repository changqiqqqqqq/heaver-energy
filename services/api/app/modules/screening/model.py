"""免费用能初筛模型。"""

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.common.datetime import utc_now
from app.db.base import Base

IdType = BigInteger().with_variant(Integer, "sqlite")


class ScreeningRequest(Base):
    __tablename__ = "screening_requests"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(IdType, nullable=False)
    enterprise_id: Mapped[int | None] = mapped_column(ForeignKey("enterprises.id"))
    lead_id: Mapped[int | None] = mapped_column(ForeignKey("leads.id"))
    submission_id: Mapped[int | None] = mapped_column(ForeignKey("questionnaire_submissions.id"))
    region_text: Mapped[str | None] = mapped_column(String(128))
    enterprise_name: Mapped[str | None] = mapped_column(String(128))
    enterprise_type: Mapped[str | None] = mapped_column(String(64))
    monthly_kwh_range: Mapped[str | None] = mapped_column(String(32))
    contact_name: Mapped[str | None] = mapped_column(String(64))
    contact_phone_masked: Mapped[str | None] = mapped_column(String(32))
    contact_phone_cipher: Mapped[str | None] = mapped_column(String(512))
    contact_phone_hash: Mapped[str | None] = mapped_column(String(64))
    bill_upload_status: Mapped[str] = mapped_column(String(32), default="not_uploaded", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="submitted", nullable=False)
    extra_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    __table_args__ = (
        Index("idx_screening_lead", "lead_id"),
        Index("idx_screening_enterprise", "enterprise_id"),
        Index("idx_screening_status", "status"),
        Index("idx_screening_phone_hash", "contact_phone_hash"),
    )

