from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Text
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    google_sub = Column(Text, unique=True, nullable=False)
    email = Column(Text)
    name = Column(Text)
    profile_picture_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    is_onboarded = Column(Boolean, default=False)