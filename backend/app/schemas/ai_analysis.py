from pydantic import BaseModel
from typing import List

class AIAnalysisResult(BaseModel):
    required_skills: List[str]
    difficulty: str
    task_type: str
    estimated_hours: int
    complexity_notes: str
