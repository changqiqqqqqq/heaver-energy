"""认证依赖函数。"""

from typing import Annotated

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.security import TokenError, extract_bearer_token
from app.db.session import get_db
from app.modules.auth import service
from app.modules.auth.model import AdminUser
from app.modules.user.model import AppUser


def get_current_app_user(
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
) -> AppUser:
    try:
        token = extract_bearer_token(authorization)
        return service.get_app_user_by_token(db, token)
    except (TokenError, service.AuthServiceError) as exc:
        status_code = exc.status_code if isinstance(exc, service.AuthServiceError) else 401
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc


def get_current_admin_user(
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
) -> AdminUser:
    try:
        token = extract_bearer_token(authorization)
        return service.get_admin_by_token(db, token)
    except (TokenError, service.AuthServiceError) as exc:
        status_code = exc.status_code if isinstance(exc, service.AuthServiceError) else 401
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
