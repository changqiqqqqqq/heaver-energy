"""文件元数据接口模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FileCreateRequest(BaseModel):
    biz_type: str = Field(max_length=32)
    biz_id: int | None = None
    object_key: str = Field(max_length=512)
    original_filename: str | None = Field(default=None, max_length=256)
    mime_type: str | None = Field(default=None, max_length=128)
    file_size: int | None = Field(default=None, ge=0)
    sha256: str | None = Field(default=None, max_length=64)
    sensitivity_level: str = Field(default="normal", max_length=32)
    access_policy: str = Field(default="private", max_length=32)


class FileResponse(BaseModel):
    id: int
    biz_type: str
    biz_id: int | None
    storage_provider: str
    object_key: str
    original_filename: str | None
    mime_type: str | None
    file_size: int | None
    sha256: str | None
    sensitivity_level: str
    access_policy: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FileAccessResponse(BaseModel):
    file_id: int
    object_key: str
    access_url: str

