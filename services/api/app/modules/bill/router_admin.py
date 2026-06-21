from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.response import ApiResponse
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_admin_user
from app.modules.auth.model import AdminUser
from app.modules.bill.repository import list_bill_uploads_by_lead
from app.modules.bill.schema import BillUploadResponse

router = APIRouter()


@router.get("/by-lead/{lead_id}", response_model=ApiResponse[list[BillUploadResponse]])
def list_by_lead(
    lead_id: int,
    _current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[list[BillUploadResponse]]:
    return ApiResponse(data=[BillUploadResponse.model_validate(item) for item in list_bill_uploads_by_lead(db, lead_id)])

