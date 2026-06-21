"""安全审计接口模型。"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AuditLogCreate(BaseModel):
    actor_type: str = "admin"
    actor_id: int | None = None
    action: str = Field(max_length=128)
    target_type: str | None = Field(default=None, max_length=64)
    target_id: int | None = None
    ip_address: str | None = Field(default=None, max_length=64)
    user_agent: str | None = Field(default=None, max_length=512)
    request_id: str | None = Field(default=None, max_length=64)
    detail: dict[str, Any] | None = None


class AuditLogResponse(BaseModel):
    id: int
    actor_type: str
    actor_id: int | None
    action: str
    target_type: str | None
    target_id: int | None
    ip_address: str | None
    user_agent: str | None
    request_id: str | None
    detail_json: dict[str, Any] | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

