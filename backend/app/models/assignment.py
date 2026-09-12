from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from app.database import Base

class Assignment(Base):
    __tablename__ = 'assignments'

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id'))
    employee_id: Mapped[int] = mapped_column(ForeignKey('employees.id'))
    assigned_at: Mapped[datetime] = mapped_column(server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(50), default='active')

    task = relationship("Task", back_populates="assignments")
    employee = relationship("Employee", back_populates="assignments")
