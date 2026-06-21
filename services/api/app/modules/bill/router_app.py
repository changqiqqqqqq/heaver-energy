from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.common.response import ApiResponse
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_app_user
from app.modules.bill import service
from app.modules.bill.schema import BillUploadCreateRequest, BillUploadResponse
from app.modules.user.model import AppUser

router = APIRouter()


@router.post("", response_model=ApiResponse[BillUploadResponse])
def create_bill_upload(
    request_body: BillUploadCreateRequest,
    current_user: Annotated[AppUser, Depends(get_current_app_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[BillUploadResponse]:
    try:
        data = service.create_bill_upload(db, user=current_user, request=request_body)
    except service.BillServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=data)

