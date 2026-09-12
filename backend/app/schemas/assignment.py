from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class AssignmentBase(BaseModel):
    task_id: int
    employee_id: int

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentRead(AssignmentBase):
    id: int
    assigned_at: datetime
    completed_at: Optional[datetime] = None
    status: str

    model_config = ConfigDict(from_attributes=True)
