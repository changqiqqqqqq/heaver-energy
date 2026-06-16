"""小程序端认证接口。"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.common.response import ApiResponse
from app.db.session import get_db
from app.modules.auth import service
from app.modules.auth.dependencies import get_current_app_user
from app.modules.auth.schema import (
    AppPhoneAuthorizeRequest,
    AppWechatLoginRequest,
    AuthTokenResponse,
    AuthUserResponse,
    PhoneAuthorizeResponse,
)
from app.modules.user.model import AppUser

router = APIRouter()


@router.post("/wechat-login", response_model=ApiResponse[AuthTokenResponse])
def wechat_login(
    request_body: AppWechatLoginRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[AuthTokenResponse]:
    try:
        data = service.login_with_wechat(db, request_body)
    except service.AuthServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=data)


@router.post("/phone-authorize", response_model=ApiResponse[PhoneAuthorizeResponse])
def authorize_phone(
    request_body: AppPhoneAuthorizeRequest,
    request: Request,
    current_user: Annotated[AppUser, Depends(get_current_app_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[PhoneAuthorizeResponse]:
    try:
        data = service.authorize_phone(
            db,
            user=current_user,
            request=request_body,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except service.AuthServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=data)


@router.get("/me", response_model=ApiResponse[AuthUserResponse])
def get_me(current_user: Annotated[AppUser, Depends(get_current_app_user)]) -> ApiResponse[AuthUserResponse]:
    return ApiResponse(data=service.build_app_user_response(current_user))
