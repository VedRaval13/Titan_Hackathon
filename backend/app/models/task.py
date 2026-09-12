from sqlalchemy import Column, String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from app.database import Base


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    jira_issue_key: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(50), default='medium')
    deadline: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(50), default='open')
    task_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    required_skills = Column(JSON, default=[])
    difficulty_score: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    assigned_employee_id: Mapped[Optional[int]] = mapped_column(ForeignKey('employees.id'), nullable=True)
    ai_analysis = Column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    assigned_employee = relationship("Employee", foreign_keys=[assigned_employee_id])
    recommendations = relationship("Recommendation", back_populates="task")
    assignments = relationship("Assignment", back_populates="task")
