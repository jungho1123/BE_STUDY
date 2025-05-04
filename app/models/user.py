# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.core.time import get_kst_now

# from .nose import NoseVector # 순환 참조 방지를 위해 직접 임포트 대신 문자열 참조 권장

class User(Base):
    """
    애플리케이션의 사용자 계정을 나타내는 모델입니다.
    각 사용자는 고유한 ID를 가지며, 비문 데이터와 연결될 수 있습니다.
    """
    __tablename__ = "users"

    # 사용자의 고유 식별자 (Primary Key)
    user_id = Column(Integer, primary_key=True, index=True, name="id") # 변수명은 user_id로, 컬럼명은 id로 유지
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=get_kst_now, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # 이 사용자와 관련된 NoseVector 레코드 목록
    # relationship 정의 시 문자열 'NoseVector' 사용
    user_nose_vectors = relationship("NoseVector", back_populates="user") # 변수명 변경

    def __repr__(self):
        """
        User 객체의 표현을 반환합니다.
        """
        return f"<User(user_id={self.user_id}, username='{self.username}')>"