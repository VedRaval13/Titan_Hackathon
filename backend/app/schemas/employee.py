from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class EmployeeBase(BaseModel):
    name: str
    email: str
    skills: List[str] = []
    experience_years: int = 0
    department: Optional[str] = None
    availability_status: str = 'available'
    current_workload_score: float = 0.0

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    department: Optional[str] = None
    availability_status: Optional[str] = None
    current_workload_score: Optional[float] = None

class EmployeeRead(EmployeeBase):
    id: int
    past_task_ids: List[int] = []
    jira_account_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WorkloadSummary(BaseModel):
    employee_id: int
    name: str
    current_workload_score: float
    active_task_count: int
    availability_status: str
