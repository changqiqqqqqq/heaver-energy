"""服务需求接口模型。"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ServiceRequestItemInput(BaseModel):
    need_type: str = Field(max_length=32)
    need_name: str = Field(max_length=64)
    extra: dict[str, Any] = Field(default_factory=dict)


class ServiceRequestSubmitRequest(BaseModel):
    lead_id: int | None = None
    enterprise_id: int | None = None
    submission_id: int | None = None
    primary_need_type: str | None = Field(default=None, max_length=32)
    description: str | None = Field(default=None, max_length=512)
    items: list[ServiceRequestItemInput] = Field(min_length=1)


class ServiceRequestItemResponse(BaseModel):
    id: int
    service_request_id: int
    need_type: str
    need_name: str
    extra_json: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)


class ServiceRequestResponse(BaseModel):
    id: int
    request_no: str
    user_id: int
    enterprise_id: int | None
    lead_id: int | None
    primary_need_type: str | None
    description: str | None
    status: str
    submitted_at: datetime
    items: list[ServiceRequestItemResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

