"""免费初筛业务服务。"""

from sqlalchemy.orm import Session

from app.core.security import hash_phone, mask_phone, normalize_phone
from app.modules.enterprise.schema import EnterpriseContactUpsertRequest, EnterpriseUpsertRequest
from app.modules.enterprise.service import create_or_update_enterprise, create_or_update_primary_contact
from app.modules.lead.schema import LeadInternalUpsert
from app.modules.lead.service import create_or_update_lead
from app.modules.screening import repository
from app.modules.screening.model import ScreeningRequest
from app.modules.screening.schema import ScreeningResponse, ScreeningSubmitRequest
from app.modules.user.model import AppUser


class ScreeningServiceError(ValueError):
    """初筛业务错误。"""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def submit_screening(db: Session, *, user: AppUser, request: ScreeningSubmitRequest) -> ScreeningResponse:
    enterprise = create_or_update_enterprise(
        db,
        owner_user_id=user.id,
        enterprise_id=request.enterprise_id,
        request=EnterpriseUpsertRequest(
            name=request.enterprise_name,
            region_tag=request.region_text,
            industry_type=request.enterprise_type,
            monthly_kwh_range=request.monthly_kwh_range,
        ),
    )
    create_or_update_primary_contact(
        db,
        enterprise_id=enterprise.id,
        request=EnterpriseContactUpsertRequest(
            name=request.contact_name,
            phone_number=request.contact_phone,
        ),
    )

    phone_masked = None
    phone_hash = None
    if request.contact_phone:
        try:
            phone = normalize_phone(request.contact_phone)
        except ValueError as exc:
            raise ScreeningServiceError("手机号格式不正确", status_code=400) from exc
        phone_masked = mask_phone(phone)
        phone_hash = hash_phone(phone)

    lead = create_or_update_lead(
        db,
        LeadInternalUpsert(
            user_id=user.id,
            enterprise_id=enterprise.id,
            lead_id=request.lead_id,
            source_entry="screening",
            has_phone_authorized=bool(phone_hash or user.phone_hash),
        ),
    )
    screening = repository.add_screening(
        db,
        ScreeningRequest(
            user_id=user.id,
            enterprise_id=enterprise.id,
            lead_id=lead.id,
            submission_id=request.submission_id,
            region_text=request.region_text,
            enterprise_name=request.enterprise_name,
            enterprise_type=request.enterprise_type,
            monthly_kwh_range=request.monthly_kwh_range,
            contact_name=request.contact_name,
            contact_phone_masked=phone_masked,
            contact_phone_hash=phone_hash,
            extra_json=request.extra,
        ),
    )
    db.commit()
    db.refresh(screening)
    return ScreeningResponse.model_validate(screening)

