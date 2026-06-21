"""服务需求模型。"""

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.datetime import utc_now
from app.db.base import Base

IdType = BigInteger().with_variant(Integer, "sqlite")


class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    request_no: Mapped[str] = mapped_column(String(32), nullable=False)
    user_id: Mapped[int] = mapped_column(IdType, nullable=False)
    enterprise_id: Mapped[int | None] = mapped_column(ForeignKey("enterprises.id"))
    lead_id: Mapped[int | None] = mapped_column(ForeignKey("leads.id"))
    submission_id: Mapped[int | None] = mapped_column(ForeignKey("questionnaire_submissions.id"))
    primary_need_type: Mapped[str | None] = mapped_column(String(32))
    description: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), default="submitted", nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    items: Mapped[list["ServiceRequestItem"]] = relationship(
        back_populates="service_request",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("uk_service_requests_no", "request_no", unique=True),
        Index("idx_service_requests_lead", "lead_id"),
        Index("idx_service_requests_need_status", "primary_need_type", "status"),
    )


class ServiceRequestItem(Base):
    __tablename__ = "service_request_items"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    service_request_id: Mapped[int] = mapped_column(ForeignKey("service_requests.id"), nullable=False)
    need_type: Mapped[str] = mapped_column(String(32), nullable=False)
    need_name: Mapped[str] = mapped_column(String(64), nullable=False)
    extra_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    service_request: Mapped[ServiceRequest] = relationship(back_populates="items")

    __table_args__ = (
        Index("idx_service_items_request", "service_request_id"),
        Index("idx_service_items_need_type", "need_type"),
    )

