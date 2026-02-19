from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from database import Base


# --- SQLAlchemy ORM Model ---

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)         # 1–5
    response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    responded_at = Column(DateTime, nullable=True)


# --- Pydantic Schemas ---

class FeedbackCreate(BaseModel):
    name: str
    email: str
    message: str
    rating: int                                      # 1–5


class FeedbackResponseCreate(BaseModel):
    response: str


class FeedbackOut(BaseModel):
    id: int
    name: str
    email: str
    message: str
    rating: int
    response: Optional[str] = None
    created_at: datetime
    responded_at: Optional[datetime] = None

    class Config:
        from_attributes = True
