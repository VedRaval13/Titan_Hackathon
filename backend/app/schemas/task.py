from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = 'medium'
    deadline: Optional[datetime] = None
    task_type: Optional[str] = None
    required_skills: List[str] = []

class TaskCreate(TaskBase):
    jira_issue_key: Optional[str] = None
    push_to_jira: bool = False

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    deadline: Optional[datetime] = None
    task_type: Optional[str] = None
    required_skills: Optional[List[str]] = None
    status: Optional[str] = None

class TaskRead(TaskBase):
    id: int
    jira_issue_key: Optional[str] = None
    status: str
    difficulty_score: Optional[str] = None
    assigned_employee_id: Optional[int] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
