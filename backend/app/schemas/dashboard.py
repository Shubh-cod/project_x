"""Dashboard & analytics schemas."""
from pydantic import BaseModel


class SummaryStats(BaseModel):
    total_contacts: int
    open_leads: int
    deals_won_this_month: int
    tasks_due_today: int


class PipelineValueByStage(BaseModel):
    stage: str
    count: int
    total_value: float


class AgentPerformance(BaseModel):
    user_id: str
    full_name: str
    deals_won: int
    leads_contacted: int


class DashboardResponse(BaseModel):
    summary: SummaryStats
    pipeline_by_stage: list[PipelineValueByStage]
    agent_performance: list[AgentPerformance]
