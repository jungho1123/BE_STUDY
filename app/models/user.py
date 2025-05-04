# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.core.time import get_kst_now

# Note: Importing NoseVector here creates a circular dependency
# if NoseVector also imports User using a direct import.
# Using string names in relationships ('NoseVector') is often preferred
# in models to avoid this.
# from .nose import NoseVector

class User(Base):
    """
    Represents a user in the application.

    Users are associated with nose vectors and have standard authentication
    fields like username, email, and a hashed password.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=get_kst_now, nullable=False) # nullable=False 추가
    is_active = Column(Boolean, default=True, nullable=False) # nullable=False 추가

    # Define the relationship to NoseVector.
    # Use string literal 'NoseVector' to avoid circular import issues.
    # 'back_populates' ensures a two-way relationship.
    nose_vectors = relationship("NoseVector", back_populates="user")

    def __repr__(self):
        """
        Provides a helpful representation of the User object for debugging.
        """
        return f"<User(id={self.id}, username='{self.username}')>"

# 순환 참조를 피하기 위해 model 파일에서는 다른 model을 직접 import하기보다
# relationship 정의 시 문자열로 참조하는 것이 일반적입니다.
# 따라서 from .nose import NoseVector 라인은 필요 없을 수 있습니다.