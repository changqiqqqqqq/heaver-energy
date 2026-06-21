"""统计看板接口模型。"""

from datetime import date

from pydantic import BaseModel, Field


class DashboardSummaryResponse(BaseModel):
    total_leads: int = 0
    today_new_leads: int = 0
    grade_counts: dict[str, int] = Field(default_factory=dict)
    pending_followup: int = 0
    transferred_supplier: int = 0
    bill_uploaded: int = 0
    phone_authorized: int = 0


class DashboardMetricCard(BaseModel):
    key: str
    label: str
    value: int
    change_rate: float = 0


class DashboardTrendItem(BaseModel):
    date: date
    visits: int = 0
    submissions: int = 0
    reports: int = 0
    consultations: int = 0


class DashboardFunnelStep(BaseModel):
    key: str
    label: str
    value: int
    conversion_rate: float = 0


class DashboardProfileDistributionItem(BaseModel):
    profile_code: str
    profile_name: str
    count: int
    ratio: float = 0
    consultation_rate: float = 0


class DashboardPendingMessageItem(BaseModel):
    lead_id: int
    lead_no: str
    display_name: str
    profile_code: str | None = None
    profile_name: str | None = None
    content: str
    status: str = "pending"
    minutes_ago: int | None = None


class DashboardOverviewResponse(BaseModel):
    date: date
    cards: list[DashboardMetricCard] = Field(default_factory=list)
    trend: list[DashboardTrendItem] = Field(default_factory=list)
    funnel: list[DashboardFunnelStep] = Field(default_factory=list)
    profile_distribution: list[DashboardProfileDistributionItem] = Field(default_factory=list)
    pending_messages: list[DashboardPendingMessageItem] = Field(default_factory=list)

