"""统计模块业务服务。"""

from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy.orm import Session

from app.modules.statistics import repository
from app.modules.statistics.schema import (
    DashboardFunnelStep,
    DashboardMetricCard,
    DashboardOverviewResponse,
    DashboardPendingMessageItem,
    DashboardProfileDistributionItem,
    DashboardSummaryResponse,
    DashboardTrendItem,
)

PROFILE_NAMES = {
    "hidden_waste": "隐性浪费型",
    "energy_awakened": "能源觉醒型",
    "supplier_confused": "供应商迷茫型",
    "cost_sensitive": "成本敏感型",
    "growth_expansion": "增长扩张型",
    "stable_operation": "稳健经营型",
}


def get_dashboard_summary(db: Session) -> DashboardSummaryResponse:
    now = datetime.now(UTC)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return DashboardSummaryResponse(
        total_leads=repository.count_leads(db),
        today_new_leads=repository.count_leads_since(db, today_start),
        grade_counts=repository.count_leads_by_grade(db),
        pending_followup=repository.count_by_status(db, "pending_followup"),
        transferred_supplier=repository.count_by_status(db, "transferred_supplier"),
        bill_uploaded=repository.count_bill_uploaded(db),
        phone_authorized=repository.count_phone_authorized(db),
    )


def _day_range(target_date: date) -> tuple[datetime, datetime]:
    start_at = datetime.combine(target_date, time.min, tzinfo=UTC)
    end_at = start_at + timedelta(days=1)
    return start_at, end_at


def _date_range(start_date: date, end_date: date) -> tuple[datetime, datetime]:
    start_at = datetime.combine(start_date, time.min, tzinfo=UTC)
    # 查询统一使用左闭右开区间，避免 MySQL DATETIME 精度导致边界重复。
    end_at = datetime.combine(end_date + timedelta(days=1), time.min, tzinfo=UTC)
    return start_at, end_at


def _round_rate(value: float) -> float:
    return round(value, 1)


def _change_rate(current: int, previous: int) -> float:
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return _round_rate((current - previous) / previous * 100)


def _conversion_rate(current: int, previous: int) -> float:
    if previous <= 0:
        return 0.0
    return _round_rate(current / previous * 100)


def _daily_trend(db: Session, *, start_date: date, end_date: date) -> list[DashboardTrendItem]:
    start_at, end_at = _date_range(start_date, end_date)
    lead_map = repository.count_leads_by_day(db, start_at, end_at)
    submission_map = repository.count_submissions_by_day(db, start_at, end_at)
    report_map = repository.count_screenings_by_day(db, start_at, end_at)
    consultation_map = repository.count_service_requests_by_day(db, start_at, end_at)

    days = (end_date - start_date).days + 1
    trend: list[DashboardTrendItem] = []
    for offset in range(days):
        current_date = start_date + timedelta(days=offset)
        key = current_date.isoformat()
        submissions = submission_map.get(key, 0)
        reports = report_map.get(key, 0)
        consultations = consultation_map.get(key, 0)
        # 当前尚未接入访问埋点，访问人数先以链路内最大行为数兜底，保证漏斗展示不倒挂。
        visits = max(lead_map.get(key, 0), submissions, reports, consultations)
        trend.append(
            DashboardTrendItem(
                date=current_date,
                visits=visits,
                submissions=submissions,
                reports=reports,
                consultations=consultations,
            )
        )
    return trend


def _profile_distribution(db: Session, *, start_at: datetime, end_at: datetime) -> list[DashboardProfileDistributionItem]:
    profile_counts = repository.count_profiles_between(db, start_at, end_at)
    consultation_counts = repository.count_consultations_by_profile_between(db, start_at, end_at)
    total = sum(profile_counts.values())
    result: list[DashboardProfileDistributionItem] = []
    for profile_code, count in sorted(profile_counts.items(), key=lambda item: item[1], reverse=True):
        result.append(
            DashboardProfileDistributionItem(
                profile_code=profile_code,
                profile_name=PROFILE_NAMES.get(profile_code, profile_code),
                count=count,
                ratio=_conversion_rate(count, total),
                consultation_rate=_conversion_rate(consultation_counts.get(profile_code, 0), count),
            )
        )
    return result


def _pending_messages(db: Session, *, limit: int) -> list[DashboardPendingMessageItem]:
    now = datetime.now(UTC)
    items: list[DashboardPendingMessageItem] = []
    for lead, enterprise_name in repository.list_pending_message_leads(db, limit):
        active_at = lead.last_activity_at or lead.created_at
        if active_at.tzinfo is None:
            active_at = active_at.replace(tzinfo=UTC)
        minutes_ago = max(0, int((now - active_at).total_seconds() // 60))
        display_name = enterprise_name or f"线索 {lead.lead_no[-6:]}"
        content = lead.result_summary or lead.primary_need_type or "用户完成测评后等待顾问跟进"
        items.append(
            DashboardPendingMessageItem(
                lead_id=lead.id,
                lead_no=lead.lead_no,
                display_name=display_name,
                profile_code=lead.profile_code,
                profile_name=PROFILE_NAMES.get(lead.profile_code or ""),
                content=content,
                minutes_ago=minutes_ago,
            )
        )
    return items


def get_dashboard_trends(db: Session, *, start_date: date, end_date: date) -> list[DashboardTrendItem]:
    return _daily_trend(db, start_date=start_date, end_date=end_date)


def get_dashboard_funnel(db: Session, *, target_date: date) -> list[DashboardFunnelStep]:
    start_at, end_at = _day_range(target_date)
    submissions = repository.count_submissions_between(db, start_at, end_at)
    reports = repository.count_screenings_between(db, start_at, end_at)
    consultations = repository.count_service_requests_between(db, start_at, end_at)
    visits = max(repository.count_leads_between(db, start_at, end_at), submissions, reports, consultations)
    raw_steps = [
        ("visits", "进入小程序", visits),
        ("submissions", "完成测评", submissions),
        ("reports", "领取报告", reports),
        ("consultations", "预约顾问", consultations),
    ]
    steps: list[DashboardFunnelStep] = []
    previous = 0
    for index, (key, label, value) in enumerate(raw_steps):
        steps.append(
            DashboardFunnelStep(
                key=key,
                label=label,
                value=value,
                conversion_rate=100.0 if index == 0 else _conversion_rate(value, previous),
            )
        )
        previous = value
    return steps


def get_dashboard_profile_distribution(db: Session, *, target_date: date) -> list[DashboardProfileDistributionItem]:
    start_at, end_at = _day_range(target_date)
    return _profile_distribution(db, start_at=start_at, end_at=end_at)


def get_dashboard_pending_messages(db: Session, *, limit: int) -> list[DashboardPendingMessageItem]:
    return _pending_messages(db, limit=limit)


def get_dashboard_overview(db: Session, *, target_date: date | None = None) -> DashboardOverviewResponse:
    current_date = target_date or datetime.now(UTC).date()
    start_at, end_at = _day_range(current_date)
    previous_start_at, previous_end_at = _day_range(current_date - timedelta(days=1))

    submissions = repository.count_submissions_between(db, start_at, end_at)
    reports = repository.count_screenings_between(db, start_at, end_at)
    consultations = repository.count_service_requests_between(db, start_at, end_at)
    visits = max(repository.count_leads_between(db, start_at, end_at), submissions, reports, consultations)

    previous_submissions = repository.count_submissions_between(db, previous_start_at, previous_end_at)
    previous_reports = repository.count_screenings_between(db, previous_start_at, previous_end_at)
    previous_consultations = repository.count_service_requests_between(db, previous_start_at, previous_end_at)
    previous_visits = max(
        repository.count_leads_between(db, previous_start_at, previous_end_at),
        previous_submissions,
        previous_reports,
        previous_consultations,
    )

    cards = [
        DashboardMetricCard(key="visits", label="今日点击人数", value=visits, change_rate=_change_rate(visits, previous_visits)),
        DashboardMetricCard(
            key="submissions",
            label="今日答题人数",
            value=submissions,
            change_rate=_change_rate(submissions, previous_submissions),
        ),
        DashboardMetricCard(key="reports", label="今日报告领取", value=reports, change_rate=_change_rate(reports, previous_reports)),
        DashboardMetricCard(
            key="consultations",
            label="顾问咨询预约",
            value=consultations,
            change_rate=_change_rate(consultations, previous_consultations),
        ),
    ]

    trend_start = current_date - timedelta(days=6)
    return DashboardOverviewResponse(
        date=current_date,
        cards=cards,
        trend=_daily_trend(db, start_date=trend_start, end_date=current_date),
        funnel=get_dashboard_funnel(db, target_date=current_date),
        profile_distribution=_profile_distribution(db, start_at=start_at, end_at=end_at),
        pending_messages=_pending_messages(db, limit=6),
    )

