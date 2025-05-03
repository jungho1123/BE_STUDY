# app/models/nose.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.core.time import get_kst_now

class NoseVector(Base):
    __tablename__ = "nose_vectors"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vector = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=get_kst_now)

    # 문자열 참조로 변경!
    user = relationship("User", back_populates="nose_vectors")
