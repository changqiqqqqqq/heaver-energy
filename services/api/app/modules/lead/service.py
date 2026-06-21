"""线索业务服务。"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.common.datetime import utc_now
from app.common.enums import LEAD_GRADES, LEAD_STATUSES
from app.common.pagination import PageResult
from app.modules.lead import repository
from app.modules.lead.model import Lead, LeadStatusLog
from app.modules.lead.schema import LeadDetailResponse, LeadInternalUpsert, LeadListItem
from app.modules.lead.schema import LeadSensitiveResponse


class LeadServiceError(ValueError):
    """线索业务错误。"""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _generate_lead_no() -> str:
    return f"LD{utc_now():%Y%m%d%H%M%S}{uuid.uuid4().hex[:6].upper()}"


def _touch_lead(lead: Lead) -> None:
    now = utc_now()
    if lead.first_submitted_at is None:
        lead.first_submitted_at = now
    lead.last_activity_at = now


def create_or_update_lead(db: Session, request: LeadInternalUpsert) -> Lead:
    if request.lead_grade is not None and request.lead_grade not in LEAD_GRADES:
        raise LeadServiceError("线索等级不合法")

    lead = repository.get_lead_by_id(db, request.lead_id) if request.lead_id else None
    if lead is None:
        lead = repository.get_latest_open_lead(db, user_id=request.user_id, enterprise_id=request.enterprise_id)
    if lead is None:
        lead = Lead(
            lead_no=_generate_lead_no(),
            user_id=request.user_id,
            enterprise_id=request.enterprise_id,
            source_entry=request.source_entry,
            lead_status="pending_followup",
        )
        repository.add_lead(db, lead)
    elif request.enterprise_id is not None and lead.enterprise_id is None:
        lead.enterprise_id = request.enterprise_id

    if request.user_id is not None and lead.user_id is None:
        lead.user_id = request.user_id
    lead.source_entry = request.source_entry or lead.source_entry
    if request.lead_grade is not None:
        lead.lead_grade = request.lead_grade
    if request.primary_need_type is not None:
        lead.primary_need_type = request.primary_need_type
    if request.profile_code is not None:
        lead.profile_code = request.profile_code
    if request.score_snapshot is not None:
        lead.score_snapshot_json = request.score_snapshot
    if request.need_tags:
        lead.need_tags_json = sorted(set([*(lead.need_tags_json or []), *request.need_tags]))
    if request.result_summary is not None:
        lead.result_summary = request.result_summary
    if request.has_bill_uploaded is not None:
        lead.has_bill_uploaded = request.has_bill_uploaded
    if request.has_phone_authorized is not None:
        lead.has_phone_authorized = request.has_phone_authorized

    _touch_lead(lead)
    db.add(lead)
    db.flush()
    return lead


def update_lead_status(
    db: Session,
    *,
    lead_id: int,
    to_status: str,
    operator_admin_id: int | None,
    remark: str | None = None,
) -> Lead:
    if to_status not in LEAD_STATUSES:
        raise LeadServiceError("线索状态不合法")
    lead = repository.get_lead_by_id(db, lead_id)
    if lead is None:
        raise LeadServiceError("线索不存在", status_code=404)
    if lead.lead_status != to_status:
        repository.add_status_log(
            db,
            LeadStatusLog(
                lead_id=lead.id,
                from_status=lead.lead_status,
                to_status=to_status,
                operator_admin_id=operator_admin_id,
                remark=remark,
            ),
        )
        lead.lead_status = to_status
    _touch_lead(lead)
    db.add(lead)
    db.flush()
    return lead


def _list_item(lead: Lead, enterprise_name: str | None) -> LeadListItem:
    return LeadListItem(
        id=lead.id,
        lead_no=lead.lead_no,
        enterprise_id=lead.enterprise_id,
        enterprise_name=enterprise_name,
        source_entry=lead.source_entry,
        lead_grade=lead.lead_grade,
        lead_status=lead.lead_status,
        primary_need_type=lead.primary_need_type,
        profile_code=lead.profile_code,
        result_summary=lead.result_summary,
        has_bill_uploaded=lead.has_bill_uploaded,
        has_phone_authorized=lead.has_phone_authorized,
        last_activity_at=lead.last_activity_at,
        created_at=lead.created_at,
    )


def list_admin_leads(
    db: Session,
    *,
    page: int,
    page_size: int,
    lead_grade: str | None = None,
    lead_status: str | None = None,
    profile_code: str | None = None,
    primary_need_type: str | None = None,
    has_bill_uploaded: bool | None = None,
    has_phone_authorized: bool | None = None,
) -> PageResult[LeadListItem]:
    rows, total = repository.list_leads(
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
    return PageResult(
        items=[_list_item(lead, enterprise_name) for lead, enterprise_name in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


def _json_safe_model(item: Any, fields: tuple[str, ...]) -> dict[str, Any]:
    return {field: getattr(item, field) for field in fields}


def get_admin_lead_detail(db: Session, lead_id: int) -> LeadDetailResponse:
    lead_row = repository.get_lead_with_enterprise_name(db, lead_id)
    if lead_row is None:
        raise LeadServiceError("线索不存在", status_code=404)
    lead, enterprise_name = lead_row

    # 详情页按线索 ID 做少量分表查询，避免列表接口加载大对象。
    from app.modules.bill.repository import list_bill_uploads_by_lead
    from app.modules.crm.repository import list_followups_by_lead, list_notes_by_lead
    from app.modules.questionnaire.repository import list_submissions_by_lead
    from app.modules.screening.repository import list_screenings_by_lead
    from app.modules.service_request.repository import list_service_requests_by_lead
    from app.modules.supplier.repository import list_transfers_by_lead

    submissions = [
        _json_safe_model(
            item,
            (
                "id",
                "profile_code",
                "lead_grade",
                "total_score",
                "dimension_scores_json",
                "dimension_stars_json",
                "created_at",
            ),
        )
        for item in list_submissions_by_lead(db, lead.id)
    ]
    screenings = [
        _json_safe_model(item, ("id", "region_text", "enterprise_name", "enterprise_type", "status", "submitted_at"))
        for item in list_screenings_by_lead(db, lead.id)
    ]
    service_requests = [
        _json_safe_model(item, ("id", "request_no", "primary_need_type", "description", "status", "submitted_at"))
        for item in list_service_requests_by_lead(db, lead.id)
    ]
    bill_uploads = [
        _json_safe_model(item, ("id", "file_id", "bill_month", "upload_source", "parse_status", "created_at"))
        for item in list_bill_uploads_by_lead(db, lead.id)
    ]
    followups = [
        _json_safe_model(item, ("id", "admin_id", "followup_type", "followup_result", "content", "next_followup_at"))
        for item in list_followups_by_lead(db, lead.id)
    ]
    notes = [_json_safe_model(item, ("id", "admin_id", "note_type", "content", "created_at")) for item in list_notes_by_lead(db, lead.id)]
    transfers = [
        _json_safe_model(item, ("id", "supplier_id", "service_request_id", "transfer_status", "created_at"))
        for item in list_transfers_by_lead(db, lead.id)
    ]

    return LeadDetailResponse(
        id=lead.id,
        lead_no=lead.lead_no,
        enterprise_id=lead.enterprise_id,
        enterprise_name=enterprise_name,
        user_id=lead.user_id,
        source_channel=lead.source_channel,
        source_entry=lead.source_entry,
        lead_grade=lead.lead_grade,
        lead_status=lead.lead_status,
        primary_need_type=lead.primary_need_type,
        profile_code=lead.profile_code,
        score_snapshot=lead.score_snapshot_json,
        need_tags=lead.need_tags_json or [],
        result_summary=lead.result_summary,
        has_bill_uploaded=lead.has_bill_uploaded,
        has_phone_authorized=lead.has_phone_authorized,
        assigned_admin_id=lead.assigned_admin_id,
        first_submitted_at=lead.first_submitted_at,
        last_activity_at=lead.last_activity_at,
        submissions=submissions,
        screenings=screenings,
        service_requests=service_requests,
        bill_uploads=bill_uploads,
        followups=followups,
        notes=notes,
        transfers=transfers,
    )


def get_lead_sensitive(db: Session, lead_id: int) -> LeadSensitiveResponse:
    lead = repository.get_lead_by_id(db, lead_id)
    if lead is None:
        raise LeadServiceError("线索不存在", status_code=404)
    contact = None
    if lead.enterprise_id is not None:
        from app.modules.enterprise.repository import get_primary_contact

        contact = get_primary_contact(db, lead.enterprise_id)
    return LeadSensitiveResponse(
        lead_id=lead.id,
        phone_masked=contact.phone_masked if contact else None,
        phone_cipher=contact.phone_cipher if contact else None,
        contact_name=contact.name if contact else None,
    )

