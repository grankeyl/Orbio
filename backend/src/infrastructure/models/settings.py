from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.application.common.const import HistoryType
from src.infrastructure.models.base import Base
from src.infrastructure.models.user import User

from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.sql import func

class Settings(Base):
    __tablename__ = "settings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    withdraw_gift_type: Mapped[str | None] = mapped_column(String, nullable=True)
    withdraw_gift_text: Mapped[str | None] = mapped_column(String, nullable=True)
    withdraw_money_type: Mapped[str | None] = mapped_column(String, nullable=True)
    withdraw_money_text: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())