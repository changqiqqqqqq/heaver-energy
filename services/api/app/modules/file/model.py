"""文件元数据模型。"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.common.datetime import utc_now
from app.db.base import Base

IdType = BigInteger().with_variant(Integer, "sqlite")


class FileObject(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    uploader_user_id: Mapped[int | None] = mapped_column(IdType)
    uploader_admin_id: Mapped[int | None] = mapped_column(IdType)
    biz_type: Mapped[str] = mapped_column(String(32), nullable=False)
    biz_id: Mapped[int | None] = mapped_column(IdType)
    storage_provider: Mapped[str] = mapped_column(String(32), default="local", nullable=False)
    bucket: Mapped[str | None] = mapped_column(String(128))
    object_key: Mapped[str] = mapped_column(String(512), nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String(256))
    mime_type: Mapped[str | None] = mapped_column(String(128))
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    sha256: Mapped[str | None] = mapped_column(String(64))
    sensitivity_level: Mapped[str] = mapped_column(String(32), default="normal", nullable=False)
    access_policy: Mapped[str] = mapped_column(String(32), default="private", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_files_biz_type", "biz_type", "biz_id"),
        Index("idx_files_sha256", "sha256"),
    )

