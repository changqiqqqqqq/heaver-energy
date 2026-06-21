from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.common.response import ApiResponse
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_app_user
from app.modules.file import service
from app.modules.file.schema import FileCreateRequest, FileResponse
from app.modules.user.model import AppUser

router = APIRouter()


@router.post("", response_model=ApiResponse[FileResponse])
def create_file(
    request_body: FileCreateRequest,
    current_user: Annotated[AppUser, Depends(get_current_app_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[FileResponse]:
    try:
        data = service.create_app_file(db, user=current_user, request=request_body)
    except service.FileServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=data)

