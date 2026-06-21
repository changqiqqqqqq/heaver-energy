from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.common.response import ApiResponse
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_admin_user
from app.modules.auth.model import AdminUser
from app.modules.file import service
from app.modules.file.schema import FileAccessResponse
from app.modules.security_audit.schema import AuditLogCreate
from app.modules.security_audit.service import write_audit_log

router = APIRouter()


@router.get("/{file_id}/signed-url", response_model=ApiResponse[FileAccessResponse])
def get_file_access(
    file_id: int,
    request: Request,
    _current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
    user_agent: Annotated[str | None, Header()] = None,
) -> ApiResponse[FileAccessResponse]:
    try:
        data = service.get_admin_file_access(db, file_id=file_id)
        write_audit_log(
            db,
            AuditLogCreate(
                actor_id=_current_admin.id,
                action="file.signed_url",
                target_type="file",
                target_id=file_id,
                ip_address=request.client.host if request.client else None,
                user_agent=user_agent,
            ),
        )
        db.commit()
    except service.FileServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=data)

