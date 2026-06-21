"""账单上传接口模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BillUploadCreateRequest(BaseModel):
    lead_id: int | None = None
    enterprise_id: int | None = None
    file_id: int
    bill_month: str | None = Field(default=None, max_length=16)
    manual_remark: str | None = Field(default=None, max_length=512)


class BillUploadResponse(BaseModel):
    id: int
    enterprise_id: int | None
    lead_id: int | None
    file_id: int
    bill_month: str | None
    upload_source: str
    parse_status: str
    manual_remark: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

