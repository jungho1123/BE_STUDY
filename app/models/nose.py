# app/models/nose.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.core.time import get_kst_now

class NoseVector(Base):
    """
    강아지 비문 특징 벡터와 관련 정보를 저장하는 모델입니다.
    각 레코드는 추출된 하나의 비문 벡터를 나타냅니다.
    """
    __tablename__ = "nose_vectors"

    # 이 테이블 레코드 자체의 고유 식별자 (Primary Key)
    # 비문 벡터 레코드 하나하나를 식별하는 번호입니다.
    nose_vector_record_id = Column(Integer, primary_key=True, index=True, name="id") # 변수명 변경, 컬럼명은 id 유지

    # 이 비문 벡터가 속한 사용자의 ID (ForeignKey)
    # User 모델의 user_id (DB 컬럼명 id)를 참조합니다.
    associated_user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # 변수명 변경

    # 특정 강아지의 비문을 논리적으로 식별하는 고유 식별자.
    # 같은 강아지의 다른 비문 벡터들이 있다면 동일한 이 값을 가질 수 있습니다 (unique=True 제거 시).
    # 현재 unique=True 이므로, 하나의 class_id는 하나의 NoseVector 레코드에만 연결됩니다.
    dog_non_print_identifier = Column(String, unique=True, nullable=False, index=True, name="class_id") # 변수명 변경, 컬럼명은 class_id 유지

    # 이미지에서 추출되어 정규화된 512차원의 특징 벡터 (JSON 형식)
    feature_vector = Column(JSON, nullable=False, name="vector") # 변수명 변경, 컬럼명은 vector 유지

    created_at = Column(DateTime, default=get_kst_now, nullable=False)

    # 이 비문 벡터 레코드가 속한 User 객체
    # relationship 정의 시 문자열 'User' 사용
    user = relationship("User", back_populates="user_nose_vectors") # relationship 이름 업데이트

    def __repr__(self):
        """
        NoseVector 객체의 표현을 반환합니다.
        """
        return f"<NoseVector(id={self.nose_vector_record_id}, identifier='{self.dog_non_print_identifier}', user_id={self.associated_user_id})>"