from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.common.response import ApiResponse
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_admin_user
from app.modules.auth.model import AdminUser
from app.modules.enterprise import repository
from app.modules.enterprise.schema import EnterpriseResponse

router = APIRouter()


@router.get("/{enterprise_id}", response_model=ApiResponse[EnterpriseResponse])
def get_enterprise(
    enterprise_id: int,
    _current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[EnterpriseResponse]:
    enterprise = repository.get_enterprise_by_id(db, enterprise_id)
    if enterprise is None:
        raise HTTPException(status_code=404, detail="企业不存在")
    return ApiResponse(data=EnterpriseResponse.model_validate(enterprise))

