"""服务需求数据访问。"""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.service_request.model import ServiceRequest, ServiceRequestItem


def add_service_request(db: Session, service_request: ServiceRequest) -> ServiceRequest:
    db.add(service_request)
    db.flush()
    return service_request


def add_service_request_item(db: Session, item: ServiceRequestItem) -> ServiceRequestItem:
    db.add(item)
    db.flush()
    return item


def get_service_request_detail(db: Session, request_id: int) -> ServiceRequest | None:
    statement = (
        select(ServiceRequest)
        .options(selectinload(ServiceRequest.items))
        .where(ServiceRequest.id == request_id, ServiceRequest.deleted_at.is_(None))
    )
    return db.scalar(statement)


def list_service_requests_by_lead(db: Session, lead_id: int) -> list[ServiceRequest]:
    statement = (
        select(ServiceRequest)
        .options(selectinload(ServiceRequest.items))
        .where(ServiceRequest.lead_id == lead_id, ServiceRequest.deleted_at.is_(None))
        .order_by(ServiceRequest.submitted_at.desc())
    )
    return list(db.scalars(statement).all())

