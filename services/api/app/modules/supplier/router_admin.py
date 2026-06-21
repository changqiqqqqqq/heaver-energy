from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.common.response import ApiResponse
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_admin_user
from app.modules.auth.model import AdminUser
from app.modules.supplier import service
from app.modules.supplier.schema import (
    SupplierCreateRequest,
    SupplierResponse,
    SupplierTransferCreateRequest,
    SupplierTransferResponse,
)

router = APIRouter()


@router.get("", response_model=ApiResponse[list[SupplierResponse]])
def list_suppliers(
    _current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[list[SupplierResponse]]:
    return ApiResponse(data=service.list_admin_suppliers(db))


@router.post("", response_model=ApiResponse[SupplierResponse])
def create_supplier(
    request_body: SupplierCreateRequest,
    _current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[SupplierResponse]:
    return ApiResponse(data=service.create_supplier(db, request_body))


@router.post("/transfers", response_model=ApiResponse[SupplierTransferResponse])
def transfer_lead(
    request_body: SupplierTransferCreateRequest,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[SupplierTransferResponse]:
    try:
        data = service.transfer_lead(db, admin=current_admin, request=request_body)
    except service.SupplierServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=data)

