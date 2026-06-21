from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.common.response import ApiResponse
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_app_user
from app.modules.enterprise import service
from app.modules.enterprise.schema import EnterpriseResponse, EnterpriseUpsertRequest
from app.modules.user.model import AppUser

router = APIRouter()


@router.post("", response_model=ApiResponse[EnterpriseResponse])
def upsert_enterprise(
    request_body: EnterpriseUpsertRequest,
    current_user: Annotated[AppUser, Depends(get_current_app_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[EnterpriseResponse]:
    try:
        enterprise = service.create_or_update_enterprise(db, owner_user_id=current_user.id, request=request_body)
        db.commit()
        db.refresh(enterprise)
    except service.EnterpriseServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=EnterpriseResponse.model_validate(enterprise))

