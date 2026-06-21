"""线索接口模型。"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LeadListItem(BaseModel):
    id: int
    lead_no: str
    enterprise_id: int | None
    enterprise_name: str | None = None
    source_entry: str | None
    lead_grade: str | None
    lead_status: str
    primary_need_type: str | None
    profile_code: str | None
    result_summary: str | None
    has_bill_uploaded: bool
    has_phone_authorized: bool
    last_activity_at: datetime | None
    created_at: datetime


class LeadDetailResponse(BaseModel):
    id: int
    lead_no: str
    enterprise_id: int | None
    enterprise_name: str | None = None
    user_id: int | None
    source_channel: str
    source_entry: str | None
    lead_grade: str | None
    lead_status: str
    primary_need_type: str | None
    profile_code: str | None
    score_snapshot: dict[str, Any] | None = None
    need_tags: list[str] = Field(default_factory=list)
    result_summary: str | None
    has_bill_uploaded: bool
    has_phone_authorized: bool
    assigned_admin_id: int | None
    first_submitted_at: datetime | None
    last_activity_at: datetime | None
    submissions: list[dict[str, Any]] = Field(default_factory=list)
    screenings: list[dict[str, Any]] = Field(default_factory=list)
    service_requests: list[dict[str, Any]] = Field(default_factory=list)
    bill_uploads: list[dict[str, Any]] = Field(default_factory=list)
    followups: list[dict[str, Any]] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    transfers: list[dict[str, Any]] = Field(default_factory=list)


class LeadStatusUpdateRequest(BaseModel):
    lead_status: str = Field(max_length=32)
    remark: str | None = Field(default=None, max_length=512)


class LeadInternalUpsert(BaseModel):
    user_id: int | None = None
    enterprise_id: int | None = None
    lead_id: int | None = None
    source_entry: str = "questionnaire"
    lead_grade: str | None = None
    primary_need_type: str | None = None
    profile_code: str | None = None
    score_snapshot: dict[str, Any] | None = None
    need_tags: list[str] = Field(default_factory=list)
    result_summary: str | None = None
    has_bill_uploaded: bool | None = None
    has_phone_authorized: bool | None = None


class LeadSensitiveResponse(BaseModel):
    lead_id: int
    phone_masked: str | None
    phone_cipher: str | None
    contact_name: str | None


class LeadModelResponse(BaseModel):
    id: int
    lead_no: str
    lead_status: str
    lead_grade: str | None

    model_config = ConfigDict(from_attributes=True)

