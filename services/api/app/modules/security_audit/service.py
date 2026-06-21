"""安全审计业务服务。"""

from sqlalchemy.orm import Session

from app.modules.security_audit import repository
from app.modules.security_audit.model import AuditLog
from app.modules.security_audit.schema import AuditLogCreate, AuditLogResponse


def write_audit_log(db: Session, request: AuditLogCreate) -> AuditLog:
    return repository.add_audit_log(
        db,
        AuditLog(
            actor_type=request.actor_type,
            actor_id=request.actor_id,
            action=request.action,
            target_type=request.target_type,
            target_id=request.target_id,
            ip_address=request.ip_address,
            user_agent=request.user_agent,
            request_id=request.request_id,
            detail_json=request.detail,
        ),
    )


def list_admin_audit_logs(
    db: Session,
    *,
    action: str | None = None,
    target_type: str | None = None,
    target_id: int | None = None,
    limit: int = 100,
) -> list[AuditLogResponse]:
    return [
        AuditLogResponse.model_validate(item)
        for item in repository.list_audit_logs(
            db,
            action=action,
            target_type=target_type,
            target_id=target_id,
            limit=limit,
        )
    ]

