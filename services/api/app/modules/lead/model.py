"""线索主表和状态流转模型。"""

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.common.datetime import utc_now
from app.db.base import Base

IdType = BigInteger().with_variant(Integer, "sqlite")


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    lead_no: Mapped[str] = mapped_column(String(32), nullable=False)
    enterprise_id: Mapped[int | None] = mapped_column(ForeignKey("enterprises.id"))
    user_id: Mapped[int | None] = mapped_column(IdType)
    source_channel: Mapped[str] = mapped_column(String(64), default="miniapp", nullable=False)
    source_entry: Mapped[str | None] = mapped_column(String(64))
    lead_grade: Mapped[str | None] = mapped_column(String(16))
    lead_status: Mapped[str] = mapped_column(String(32), default="pending_followup", nullable=False)
    primary_need_type: Mapped[str | None] = mapped_column(String(32))
    profile_code: Mapped[str | None] = mapped_column(String(64))
    score_snapshot_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    need_tags_json: Mapped[list[str] | None] = mapped_column(JSON)
    result_summary: Mapped[str | None] = mapped_column(String(512))
    has_bill_uploaded: Mapped[bool] = mapped_column(default=False, nullable=False)
    has_phone_authorized: Mapped[bool] = mapped_column(default=False, nullable=False)
    assigned_admin_id: Mapped[int | None] = mapped_column(IdType)
    first_submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_activity_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("uk_leads_lead_no", "lead_no", unique=True),
        Index("idx_leads_user", "user_id", "created_at"),
        Index("idx_leads_enterprise", "enterprise_id"),
        Index("idx_leads_grade_status", "lead_grade", "lead_status"),
        Index("idx_leads_profile_grade", "profile_code", "lead_grade"),
        Index("idx_leads_need_type", "primary_need_type"),
        Index("idx_leads_last_activity", "last_activity_at"),
        Index("idx_leads_assigned_admin", "assigned_admin_id"),
    )


class LeadStatusLog(Base):
    __tablename__ = "lead_status_logs"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(32))
    to_status: Mapped[str] = mapped_column(String(32), nullable=False)
    operator_admin_id: Mapped[int | None] = mapped_column(IdType)
    operator_type: Mapped[str] = mapped_column(String(32), default="admin", nullable=False)
    remark: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (Index("idx_lead_status_logs_lead", "lead_id", "created_at"),)

