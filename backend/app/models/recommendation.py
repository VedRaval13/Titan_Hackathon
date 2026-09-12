from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base

class Recommendation(Base):
    __tablename__ = 'recommendations'

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id'))
    recommended_employee_id: Mapped[int] = mapped_column(ForeignKey('employees.id'))
    match_score: Mapped[float]
    reason: Mapped[str] = mapped_column(Text)
    confidence_level: Mapped[str] = mapped_column(String(20), default='medium')
    manager_action: Mapped[str] = mapped_column(String(20), default='pending')
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    task = relationship("Task", back_populates="recommendations")
    employee = relationship("Employee", back_populates="recommendations")
