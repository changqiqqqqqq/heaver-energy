"""认证接口请求与响应模型。"""

from pydantic import BaseModel, ConfigDict, Field


class AppWechatLoginRequest(BaseModel):
    code: str = Field(min_length=1, max_length=128)
    nickname: str | None = Field(default=None, max_length=64)
    avatar_url: str | None = Field(default=None, max_length=512)


class AppPhoneAuthorizeRequest(BaseModel):
    consent_version: str = Field(default="v1", max_length=32)
    granted: bool = True
    phone_code: str | None = Field(default=None, max_length=256)
    encrypted_data: str | None = Field(default=None, max_length=4096)
    iv: str | None = Field(default=None, max_length=128)
    dev_phone_number: str | None = Field(default=None, max_length=32)


class AuthUserResponse(BaseModel):
    id: int
    nickname: str | None = None
    avatar_url: str | None = None
    phone_masked: str | None = None
    status: str
    has_phone_authorized: bool

    model_config = ConfigDict(from_attributes=True)


class AdminUserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    phone_masked: str | None = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: AuthUserResponse


class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    admin: AdminUserResponse


class PhoneAuthorizeResponse(BaseModel):
    user: AuthUserResponse
    phone_authorized: bool


class AdminLoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)
