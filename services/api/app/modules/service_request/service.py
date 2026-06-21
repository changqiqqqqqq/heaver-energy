"""服务需求业务服务。"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.common.enums import NEED_TYPES
from app.modules.lead.schema import LeadInternalUpsert
from app.modules.lead.service import create_or_update_lead
from app.modules.service_request import repository
from app.modules.service_request.model import ServiceRequest, ServiceRequestItem
from app.modules.service_request.schema import ServiceRequestResponse, ServiceRequestSubmitRequest
from app.modules.user.model import AppUser


class ServiceRequestServiceError(ValueError):
    """服务需求业务错误。"""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _request_no() -> str:
    return f"SR{uuid.uuid4().hex[:16].upper()}"


def _response(item: ServiceRequest) -> ServiceRequestResponse:
    return ServiceRequestResponse.model_validate(item)


def submit_service_request(
    db: Session,
    *,
    user: AppUser,
    request: ServiceRequestSubmitRequest,
) -> ServiceRequestResponse:
    need_types = [item.need_type for item in request.items]
    invalid_types = [item for item in need_types if item not in NEED_TYPES]
    if invalid_types:
        raise ServiceRequestServiceError(f"不支持的需求类型：{invalid_types[0]}")

    primary_need_type = request.primary_need_type or need_types[0]
    lead = create_or_update_lead(
        db,
        LeadInternalUpsert(
            user_id=user.id,
            enterprise_id=request.enterprise_id,
            lead_id=request.lead_id,
            source_entry="service_request",
            primary_need_type=primary_need_type,
            need_tags=need_types,
            has_phone_authorized=bool(user.phone_hash),
        ),
    )
    service_request = repository.add_service_request(
        db,
        ServiceRequest(
            request_no=_request_no(),
            user_id=user.id,
            enterprise_id=request.enterprise_id or lead.enterprise_id,
            lead_id=lead.id,
            submission_id=request.submission_id,
            primary_need_type=primary_need_type,
            description=request.description,
        ),
    )
    for item in request.items:
        repository.add_service_request_item(
            db,
            ServiceRequestItem(
                service_request_id=service_request.id,
                need_type=item.need_type,
                need_name=item.need_name,
                extra_json=item.extra,
            ),
        )
    db.commit()
    detail = repository.get_service_request_detail(db, service_request.id)
    if detail is None:
        raise ServiceRequestServiceError("服务需求创建后读取失败", status_code=500)
    return _response(detail)

