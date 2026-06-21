"""CRM 业务服务。"""

from sqlalchemy.orm import Session

from app.common.enums import FOLLOWUP_RESULTS, FOLLOWUP_TYPES
from app.modules.auth.model import AdminUser
from app.modules.crm import repository
from app.modules.crm.model import LeadFollowup, LeadNote
from app.modules.crm.schema import FollowupCreateRequest, FollowupResponse, NoteCreateRequest, NoteResponse
from app.modules.lead.service import update_lead_status


class CrmServiceError(ValueError):
    """CRM 业务错误。"""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def create_followup(db: Session, *, admin: AdminUser, request: FollowupCreateRequest) -> FollowupResponse:
    if request.followup_type not in FOLLOWUP_TYPES:
        raise CrmServiceError("跟进方式不合法")
    if request.followup_result not in FOLLOWUP_RESULTS:
        raise CrmServiceError("跟进结果不合法")
    followup = repository.add_followup(
        db,
        LeadFollowup(
            lead_id=request.lead_id,
            admin_id=admin.id,
            followup_type=request.followup_type,
            followup_result=request.followup_result,
            content=request.content,
            next_followup_at=request.next_followup_at,
        ),
    )
    update_lead_status(db, lead_id=request.lead_id, to_status="following", operator_admin_id=admin.id, remark="新增跟进记录")
    db.commit()
    db.refresh(followup)
    return FollowupResponse.model_validate(followup)


def create_note(db: Session, *, admin: AdminUser, request: NoteCreateRequest) -> NoteResponse:
    note = repository.add_note(
        db,
        LeadNote(
            lead_id=request.lead_id,
            admin_id=admin.id,
            note_type=request.note_type,
            content=request.content,
        ),
    )
    update_lead_status(db, lead_id=request.lead_id, to_status="following", operator_admin_id=admin.id, remark="新增备注")
    db.commit()
    db.refresh(note)
    return NoteResponse.model_validate(note)

