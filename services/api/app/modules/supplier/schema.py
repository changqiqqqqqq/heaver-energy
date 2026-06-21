"""供应商和转接接口模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SupplierCreateRequest(BaseModel):
    name: str = Field(max_length=128)
    supplier_type: str = Field(max_length=32)
    region_scope: list[str] = Field(default_factory=list)
    service_tags: list[str] = Field(default_factory=list)
    contact_name: str | None = Field(default=None, max_length=64)
    contact_phone_masked: str | None = Field(default=None, max_length=32)
    remark: str | None = Field(default=None, max_length=512)


class SupplierResponse(BaseModel):
    id: int
    name: str
    supplier_type: str
    region_scope_json: list[str] | None = None
    service_tags_json: list[str] | None = None
    contact_name: str | None
    contact_phone_masked: str | None
    status: str
    remark: str | None

    model_config = ConfigDict(from_attributes=True)


class SupplierTransferCreateRequest(BaseModel):
    lead_id: int
    supplier_id: int
    service_request_id: int | None = None
    transfer_reason: str | None = Field(default=None, max_length=512)


class SupplierTransferResponse(BaseModel):
    id: int
    lead_id: int
    supplier_id: int
    service_request_id: int | None
    transfer_status: str
    transfer_reason: str | None
    operator_admin_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

