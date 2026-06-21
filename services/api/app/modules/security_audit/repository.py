"""安全审计数据访问。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.security_audit.model import AuditLog


def add_audit_log(db: Session, audit_log: AuditLog) -> AuditLog:
    db.add(audit_log)
    db.flush()
    return audit_log


def list_audit_logs(
    db: Session,
    *,
    action: str | None = None,
    target_type: str | None = None,
    target_id: int | None = None,
    limit: int = 100,
) -> list[AuditLog]:
    statement = select(AuditLog)
    if action:
        statement = statement.where(AuditLog.action == action)
    if target_type:
        statement = statement.where(AuditLog.target_type == target_type)
    if target_id is not None:
        statement = statement.where(AuditLog.target_id == target_id)
    return list(db.scalars(statement.order_by(AuditLog.created_at.desc()).limit(limit)).all())

