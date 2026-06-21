from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.common.response import ApiResponse
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_admin_user
from app.modules.auth.model import AdminUser
from app.modules.crm import service
from app.modules.crm.schema import FollowupCreateRequest, FollowupResponse, NoteCreateRequest, NoteResponse

router = APIRouter()


@router.post("/followups", response_model=ApiResponse[FollowupResponse])
def create_followup(
    request_body: FollowupCreateRequest,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[FollowupResponse]:
    try:
        data = service.create_followup(db, admin=current_admin, request=request_body)
    except service.CrmServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=data)


@router.post("/notes", response_model=ApiResponse[NoteResponse])
def create_note(
    request_body: NoteCreateRequest,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[NoteResponse]:
    try:
        data = service.create_note(db, admin=current_admin, request=request_body)
    except service.CrmServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=data)

