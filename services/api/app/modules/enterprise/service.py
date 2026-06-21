"""企业模块业务服务。"""

from sqlalchemy.orm import Session

from app.core.security import hash_phone, mask_phone, normalize_phone
from app.modules.enterprise import repository
from app.modules.enterprise.model import Enterprise, EnterpriseContact
from app.modules.enterprise.schema import EnterpriseContactUpsertRequest, EnterpriseUpsertRequest


class EnterpriseServiceError(ValueError):
    """企业业务错误。"""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _apply_enterprise_fields(enterprise: Enterprise, request: EnterpriseUpsertRequest) -> None:
    for field, value in request.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(enterprise, field, value)


def create_or_update_enterprise(
    db: Session,
    *,
    owner_user_id: int | None,
    enterprise_id: int | None = None,
    request: EnterpriseUpsertRequest | None = None,
) -> Enterprise:
    enterprise = repository.get_enterprise_by_id(db, enterprise_id) if enterprise_id else None
    if enterprise is None:
        enterprise = Enterprise(owner_user_id=owner_user_id)
        repository.add_enterprise(db, enterprise)
    elif enterprise.owner_user_id is None and owner_user_id is not None:
        enterprise.owner_user_id = owner_user_id

    if request is not None:
        _apply_enterprise_fields(enterprise, request)
    db.add(enterprise)
    db.flush()
    return enterprise


def create_or_update_primary_contact(
    db: Session,
    *,
    enterprise_id: int,
    request: EnterpriseContactUpsertRequest,
) -> EnterpriseContact | None:
    if not any(request.model_dump(exclude_none=True).values()):
        return None

    contact = repository.get_primary_contact(db, enterprise_id)
    if contact is None:
        contact = EnterpriseContact(enterprise_id=enterprise_id, is_primary=True)
        repository.add_contact(db, contact)

    if request.name is not None:
        contact.name = request.name
    if request.role_title is not None:
        contact.role_title = request.role_title
    if request.wechat_no is not None:
        contact.wechat_no = request.wechat_no
    if request.phone_number:
        try:
            phone = normalize_phone(request.phone_number)
        except ValueError as exc:
            raise EnterpriseServiceError("手机号格式不正确", status_code=400) from exc
        contact.phone_masked = mask_phone(phone)
        contact.phone_hash = hash_phone(phone)

    db.add(contact)
    db.flush()
    return contact

