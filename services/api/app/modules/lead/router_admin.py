from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.common.pagination import PageResult
from app.common.response import ApiResponse
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_admin_user
from app.modules.auth.model import AdminUser
from app.modules.lead import service
from app.modules.lead.schema import (
    LeadDetailResponse,
    LeadListItem,
    LeadModelResponse,
    LeadSensitiveResponse,
    LeadStatusUpdateRequest,
)
from app.modules.security_audit.schema import AuditLogCreate
from app.modules.security_audit.service import write_audit_log

router = APIRouter()


@router.get("", response_model=ApiResponse[PageResult[LeadListItem]])
def list_leads(
    _current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 20,
    lead_grade: Annotated[str | None, Query(max_length=16)] = None,
    lead_status: Annotated[str | None, Query(max_length=32)] = None,
    profile_code: Annotated[str | None, Query(max_length=64)] = None,
    primary_need_type: Annotated[str | None, Query(max_length=32)] = None,
    has_bill_uploaded: bool | None = None,
    has_phone_authorized: bool | None = None,
) -> ApiResponse[PageResult[LeadListItem]]:
    data = service.list_admin_leads(
        db,
        page=page,
        page_size=page_size,
        lead_grade=lead_grade,
        lead_status=lead_status,
        profile_code=profile_code,
        primary_need_type=primary_need_type,
        has_bill_uploaded=has_bill_uploaded,
        has_phone_authorized=has_phone_authorized,
    )
    return ApiResponse(data=data)


@router.get("/{lead_id}", response_model=ApiResponse[LeadDetailResponse])
def get_lead_detail(
    lead_id: int,
    _current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[LeadDetailResponse]:
    try:
        data = service.get_admin_lead_detail(db, lead_id)
    except service.LeadServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=data)


@router.post("/{lead_id}/status", response_model=ApiResponse[LeadModelResponse])
def update_lead_status(
    lead_id: int,
    request_body: LeadStatusUpdateRequest,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[LeadModelResponse]:
    try:
        lead = service.update_lead_status(
            db,
            lead_id=lead_id,
            to_status=request_body.lead_status,
            operator_admin_id=current_admin.id,
            remark=request_body.remark,
        )
        db.commit()
        db.refresh(lead)
    except service.LeadServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=LeadModelResponse.model_validate(lead))


@router.get("/{lead_id}/sensitive", response_model=ApiResponse[LeadSensitiveResponse])
def get_lead_sensitive(
    lead_id: int,
    request: Request,
    current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
    user_agent: Annotated[str | None, Header()] = None,
) -> ApiResponse[LeadSensitiveResponse]:
    try:
        data = service.get_lead_sensitive(db, lead_id)
        write_audit_log(
            db,
            AuditLogCreate(
                actor_id=current_admin.id,
                action="lead.view_sensitive",
                target_type="lead",
                target_id=lead_id,
                ip_address=request.client.host if request.client else None,
                user_agent=user_agent,
            ),
        )
        db.commit()
    except service.LeadServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=data)

