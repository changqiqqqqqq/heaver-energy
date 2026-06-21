from datetime import UTC, date, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi import Query
from sqlalchemy.orm import Session

from app.common.response import ApiResponse
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_admin_user
from app.modules.auth.model import AdminUser
from app.modules.statistics import service
from app.modules.statistics.schema import (
    DashboardFunnelStep,
    DashboardOverviewResponse,
    DashboardPendingMessageItem,
    DashboardProfileDistributionItem,
    DashboardSummaryResponse,
    DashboardTrendItem,
)

router = APIRouter()


@router.get("/summary", response_model=ApiResponse[DashboardSummaryResponse])
def get_dashboard_summary(
    _current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[DashboardSummaryResponse]:
    return ApiResponse(data=service.get_dashboard_summary(db))


@router.get("/overview", response_model=ApiResponse[DashboardOverviewResponse])
def get_dashboard_overview(
    _current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
    target_date: Annotated[date | None, Query(alias="date")] = None,
) -> ApiResponse[DashboardOverviewResponse]:
    return ApiResponse(data=service.get_dashboard_overview(db, target_date=target_date))


@router.get("/trends", response_model=ApiResponse[list[DashboardTrendItem]])
def get_dashboard_trends(
    _current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
    start_date: date | None = None,
    end_date: date | None = None,
) -> ApiResponse[list[DashboardTrendItem]]:
    current_date = datetime.now(UTC).date()
    actual_end = end_date or current_date
    actual_start = start_date or actual_end - timedelta(days=6)
    return ApiResponse(data=service.get_dashboard_trends(db, start_date=actual_start, end_date=actual_end))


@router.get("/funnel", response_model=ApiResponse[list[DashboardFunnelStep]])
def get_dashboard_funnel(
    _current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
    target_date: Annotated[date | None, Query(alias="date")] = None,
) -> ApiResponse[list[DashboardFunnelStep]]:
    return ApiResponse(data=service.get_dashboard_funnel(db, target_date=target_date or datetime.now(UTC).date()))


@router.get("/profile-distribution", response_model=ApiResponse[list[DashboardProfileDistributionItem]])
def get_dashboard_profile_distribution(
    _current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
    target_date: Annotated[date | None, Query(alias="date")] = None,
) -> ApiResponse[list[DashboardProfileDistributionItem]]:
    return ApiResponse(data=service.get_dashboard_profile_distribution(db, target_date=target_date or datetime.now(UTC).date()))


@router.get("/pending-messages", response_model=ApiResponse[list[DashboardPendingMessageItem]])
def get_dashboard_pending_messages(
    _current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
    limit: Annotated[int, Query(ge=1, le=50)] = 6,
) -> ApiResponse[list[DashboardPendingMessageItem]]:
    return ApiResponse(data=service.get_dashboard_pending_messages(db, limit=limit))

