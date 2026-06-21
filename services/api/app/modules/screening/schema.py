"""免费初筛接口模型。"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ScreeningSubmitRequest(BaseModel):
    lead_id: int | None = None
    submission_id: int | None = None
    enterprise_id: int | None = None
    region_text: str | None = Field(default=None, max_length=128)
    enterprise_name: str | None = Field(default=None, max_length=128)
    enterprise_type: str | None = Field(default=None, max_length=64)
    monthly_kwh_range: str | None = Field(default=None, max_length=32)
    contact_name: str | None = Field(default=None, max_length=64)
    contact_phone: str | None = Field(default=None, max_length=32)
    extra: dict[str, Any] = Field(default_factory=dict)


class ScreeningResponse(BaseModel):
    id: int
    user_id: int
    enterprise_id: int | None
    lead_id: int | None
    region_text: str | None
    enterprise_name: str | None
    enterprise_type: str | None
    monthly_kwh_range: str | None
    contact_name: str | None
    contact_phone_masked: str | None
    bill_upload_status: str
    status: str
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)

