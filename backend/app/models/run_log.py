from sqlalchemy import Column, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from app.database import Base


class RunLog(Base):
    __tablename__ = 'run_logs'

    id: Mapped[int] = mapped_column(primary_key=True)
    run_type: Mapped[str] = mapped_column(String(50))
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='success')
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
