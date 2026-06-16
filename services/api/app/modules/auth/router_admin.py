"""后台认证接口。"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.common.response import ApiResponse
from app.db.session import get_db
from app.modules.auth import service
from app.modules.auth.dependencies import get_current_admin_user
from app.modules.auth.model import AdminUser
from app.modules.auth.schema import AdminLoginRequest, AdminTokenResponse, AdminUserResponse

router = APIRouter()


@router.post("/login", response_model=ApiResponse[AdminTokenResponse])
def admin_login(
    request_body: AdminLoginRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[AdminTokenResponse]:
    try:
        data = service.login_admin(db, request_body)
    except service.AuthServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=data)


@router.get("/me", response_model=ApiResponse[AdminUserResponse])
def get_me(current_admin: Annotated[AdminUser, Depends(get_current_admin_user)]) -> ApiResponse[AdminUserResponse]:
    return ApiResponse(data=service.build_admin_user_response(current_admin))


@router.post("/logout", response_model=ApiResponse[dict[str, bool]])
def logout() -> ApiResponse[dict[str, bool]]:
    return ApiResponse(data={"logged_out": True})
