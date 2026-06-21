"""账单业务服务。"""

from sqlalchemy.orm import Session

from app.modules.bill import repository
from app.modules.bill.model import BillUpload
from app.modules.bill.schema import BillUploadCreateRequest, BillUploadResponse
from app.modules.lead.schema import LeadInternalUpsert
from app.modules.lead.service import create_or_update_lead
from app.modules.user.model import AppUser


class BillServiceError(ValueError):
    """账单业务错误。"""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def create_bill_upload(db: Session, *, user: AppUser, request: BillUploadCreateRequest) -> BillUploadResponse:
    lead = create_or_update_lead(
        db,
        LeadInternalUpsert(
            user_id=user.id,
            enterprise_id=request.enterprise_id,
            lead_id=request.lead_id,
            source_entry="bill_upload",
            has_bill_uploaded=True,
            has_phone_authorized=bool(user.phone_hash),
        ),
    )
    bill_upload = repository.add_bill_upload(
        db,
        BillUpload(
            enterprise_id=request.enterprise_id or lead.enterprise_id,
            lead_id=lead.id,
            file_id=request.file_id,
            bill_month=request.bill_month,
            manual_remark=request.manual_remark,
        ),
    )
    db.commit()
    db.refresh(bill_upload)
    return BillUploadResponse.model_validate(bill_upload)

