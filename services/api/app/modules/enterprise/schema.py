"""企业信息接口模型。"""

from pydantic import BaseModel, ConfigDict, Field


class EnterpriseUpsertRequest(BaseModel):
    name: str | None = Field(default=None, max_length=128)
    region_province: str | None = Field(default=None, max_length=32)
    region_city: str | None = Field(default=None, max_length=32)
    region_district: str | None = Field(default=None, max_length=32)
    region_tag: str | None = Field(default=None, max_length=32)
    industry_type: str | None = Field(default=None, max_length=64)
    monthly_kwh_range: str | None = Field(default=None, max_length=32)
    monthly_cost_range: str | None = Field(default=None, max_length=32)
    scale_remark: str | None = Field(default=None, max_length=128)


class EnterpriseContactUpsertRequest(BaseModel):
    name: str | None = Field(default=None, max_length=64)
    role_title: str | None = Field(default=None, max_length=64)
    phone_number: str | None = Field(default=None, max_length=32)
    wechat_no: str | None = Field(default=None, max_length=128)


class EnterpriseResponse(BaseModel):
    id: int
    owner_user_id: int | None
    name: str | None
    region_province: str | None
    region_city: str | None
    region_district: str | None
    region_tag: str | None
    industry_type: str | None
    monthly_kwh_range: str | None
    monthly_cost_range: str | None
    status: str

    model_config = ConfigDict(from_attributes=True)


class EnterpriseContactResponse(BaseModel):
    id: int
    enterprise_id: int
    name: str | None
    role_title: str | None
    phone_masked: str | None
    wechat_no: str | None
    is_primary: bool

    model_config = ConfigDict(from_attributes=True)

