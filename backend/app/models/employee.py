from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base


class Employee(Base):
    __tablename__ = 'employees'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    skills = Column(JSON, default=[])
    experience_years: Mapped[int] = mapped_column(default=0)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    availability_status: Mapped[str] = mapped_column(String(50), default='available')
    current_workload_score: Mapped[float] = mapped_column(default=0.0)
    past_task_ids = Column(JSON, default=[])
    jira_account_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    assignments = relationship("Assignment", back_populates="employee")
    recommendations = relationship("Recommendation", back_populates="employee")
