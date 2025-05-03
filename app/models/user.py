from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.database.base import Base
from app.core.time import get_kst_now
from sqlalchemy.orm import relationship
from .nose import NoseVector
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=get_kst_now)
    is_active = Column(Boolean, default=True)
    nose_vectors = relationship("NoseVector", back_populates="user")
