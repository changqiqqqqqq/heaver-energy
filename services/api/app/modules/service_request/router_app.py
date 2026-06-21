from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.common.response import ApiResponse
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_app_user
from app.modules.service_request import service
from app.modules.service_request.schema import ServiceRequestResponse, ServiceRequestSubmitRequest
from app.modules.user.model import AppUser

router = APIRouter()


@router.post("", response_model=ApiResponse[ServiceRequestResponse])
def submit_service_request(
    request_body: ServiceRequestSubmitRequest,
    current_user: Annotated[AppUser, Depends(get_current_app_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[ServiceRequestResponse]:
    try:
        data = service.submit_service_request(db, user=current_user, request=request_body)
    except service.ServiceRequestServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=data)

