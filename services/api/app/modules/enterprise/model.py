"""企业主体和联系人模型。"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.datetime import utc_now
from app.db.base import Base

IdType = BigInteger().with_variant(Integer, "sqlite")


class Enterprise(Base):
    __tablename__ = "enterprises"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    owner_user_id: Mapped[int | None] = mapped_column(IdType)
    name: Mapped[str | None] = mapped_column(String(128))
    region_province: Mapped[str | None] = mapped_column(String(32))
    region_city: Mapped[str | None] = mapped_column(String(32))
    region_district: Mapped[str | None] = mapped_column(String(32))
    region_tag: Mapped[str | None] = mapped_column(String(32))
    industry_type: Mapped[str | None] = mapped_column(String(64))
    monthly_kwh_range: Mapped[str | None] = mapped_column(String(32))
    monthly_cost_range: Mapped[str | None] = mapped_column(String(32))
    scale_remark: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    contacts: Mapped[list["EnterpriseContact"]] = relationship(
        back_populates="enterprise",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_enterprises_owner_user", "owner_user_id"),
        Index("idx_enterprises_region", "region_province", "region_city"),
        Index("idx_enterprises_region_tag", "region_tag"),
        Index("idx_enterprises_industry", "industry_type"),
    )


class EnterpriseContact(Base):
    __tablename__ = "enterprise_contacts"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    enterprise_id: Mapped[int] = mapped_column(ForeignKey("enterprises.id"), nullable=False)
    name: Mapped[str | None] = mapped_column(String(64))
    role_title: Mapped[str | None] = mapped_column(String(64))
    phone_masked: Mapped[str | None] = mapped_column(String(32))
    phone_cipher: Mapped[str | None] = mapped_column(String(512))
    phone_hash: Mapped[str | None] = mapped_column(String(64))
    wechat_no: Mapped[str | None] = mapped_column(String(128))
    is_primary: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    enterprise: Mapped[Enterprise] = relationship(back_populates="contacts")

    __table_args__ = (
        Index("idx_contacts_enterprise", "enterprise_id"),
        Index("idx_contacts_phone_hash", "phone_hash"),
    )

