"""供应商业务服务。"""

from sqlalchemy.orm import Session

from app.modules.auth.model import AdminUser
from app.modules.lead.service import update_lead_status
from app.modules.security_audit.schema import AuditLogCreate
from app.modules.security_audit.service import write_audit_log
from app.modules.supplier import repository
from app.modules.supplier.model import Supplier, SupplierTransfer
from app.modules.supplier.schema import (
    SupplierCreateRequest,
    SupplierResponse,
    SupplierTransferCreateRequest,
    SupplierTransferResponse,
)


class SupplierServiceError(ValueError):
    """供应商业务错误。"""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def list_admin_suppliers(db: Session) -> list[SupplierResponse]:
    return [SupplierResponse.model_validate(item) for item in repository.list_suppliers(db)]


def create_supplier(db: Session, request: SupplierCreateRequest) -> SupplierResponse:
    supplier = repository.add_supplier(
        db,
        Supplier(
            name=request.name,
            supplier_type=request.supplier_type,
            region_scope_json=request.region_scope,
            service_tags_json=request.service_tags,
            contact_name=request.contact_name,
            contact_phone_masked=request.contact_phone_masked,
            remark=request.remark,
        ),
    )
    db.commit()
    db.refresh(supplier)
    return SupplierResponse.model_validate(supplier)


def transfer_lead(
    db: Session,
    *,
    admin: AdminUser,
    request: SupplierTransferCreateRequest,
) -> SupplierTransferResponse:
    supplier = repository.get_supplier_by_id(db, request.supplier_id)
    if supplier is None:
        raise SupplierServiceError("供应商不存在", status_code=404)
    transfer = repository.add_transfer(
        db,
        SupplierTransfer(
            lead_id=request.lead_id,
            supplier_id=request.supplier_id,
            service_request_id=request.service_request_id,
            transfer_reason=request.transfer_reason,
            operator_admin_id=admin.id,
        ),
    )
    update_lead_status(
        db,
        lead_id=request.lead_id,
        to_status="transferred_supplier",
        operator_admin_id=admin.id,
        remark=request.transfer_reason or "转供应商",
    )
    write_audit_log(
        db,
        AuditLogCreate(
            actor_id=admin.id,
            action="lead.transfer_supplier",
            target_type="lead",
            target_id=request.lead_id,
            detail={"supplier_id": request.supplier_id, "service_request_id": request.service_request_id},
        ),
    )
    db.commit()
    db.refresh(transfer)
    return SupplierTransferResponse.model_validate(transfer)

