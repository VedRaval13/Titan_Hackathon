from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class ScoreBreakdown(BaseModel):
    skill_match: float
    experience: float
    availability: float
    workload: float
    past_work: float


class MatchResult(BaseModel):
    employee_id: int
    employee_name: str
    total_score: float
    confidence: str = "medium"
    breakdown: ScoreBreakdown
    rank: int = 0


class RecommendationRead(BaseModel):
    id: int
    task_id: int
    recommended_employee_id: int
    employee_name: Optional[str] = None
    match_score: float
    reason: str
    confidence_level: str
    manager_action: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecommendationResponse(BaseModel):
    task_id: int
    recommendations: List[RecommendationRead]


class ManagerOverride(BaseModel):
    employee_id: int
    reason: str
