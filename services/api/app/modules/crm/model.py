"""CRM 跟进和备注模型。"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.common.datetime import utc_now
from app.db.base import Base

IdType = BigInteger().with_variant(Integer, "sqlite")


class LeadFollowup(Base):
    __tablename__ = "lead_followups"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False)
    admin_id: Mapped[int] = mapped_column(IdType, nullable=False)
    followup_type: Mapped[str] = mapped_column(String(32), default="phone", nullable=False)
    followup_result: Mapped[str] = mapped_column(String(32), default="contacted", nullable=False)
    content: Mapped[str | None] = mapped_column(Text)
    next_followup_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    __table_args__ = (
        Index("idx_followups_lead", "lead_id", "created_at"),
        Index("idx_followups_admin_next", "admin_id", "next_followup_at"),
    )


class LeadNote(Base):
    __tablename__ = "lead_notes"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False)
    admin_id: Mapped[int] = mapped_column(IdType, nullable=False)
    note_type: Mapped[str] = mapped_column(String(32), default="general", nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (Index("idx_lead_notes_lead", "lead_id", "created_at"),)

