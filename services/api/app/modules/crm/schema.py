"""CRM 跟进和备注接口模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FollowupCreateRequest(BaseModel):
    lead_id: int
    followup_type: str = Field(default="phone", max_length=32)
    followup_result: str = Field(default="contacted", max_length=32)
    content: str | None = None
    next_followup_at: datetime | None = None


class FollowupResponse(BaseModel):
    id: int
    lead_id: int
    admin_id: int
    followup_type: str
    followup_result: str
    content: str | None
    next_followup_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NoteCreateRequest(BaseModel):
    lead_id: int
    note_type: str = Field(default="general", max_length=32)
    content: str


class NoteResponse(BaseModel):
    id: int
    lead_id: int
    admin_id: int
    note_type: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

