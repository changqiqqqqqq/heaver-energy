from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.common.response import ApiResponse
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_admin_user
from app.modules.auth.model import AdminUser
from app.modules.security_audit import service
from app.modules.security_audit.schema import AuditLogResponse

router = APIRouter()


@router.get("", response_model=ApiResponse[list[AuditLogResponse]])
def list_audit_logs(
    _current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
    action: Annotated[str | None, Query(max_length=128)] = None,
    target_type: Annotated[str | None, Query(max_length=64)] = None,
    target_id: int | None = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> ApiResponse[list[AuditLogResponse]]:
    return ApiResponse(
        data=service.list_admin_audit_logs(
            db,
            action=action,
            target_type=target_type,
            target_id=target_id,
            limit=limit,
        )
    )

