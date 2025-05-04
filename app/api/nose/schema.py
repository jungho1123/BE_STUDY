# app/api/nose/schema.py
from typing import Optional, List
from fastapi import UploadFile, Form
from pydantic import BaseModel, Field, ConfigDict

# 요청 시 파일과 함께 받을 데이터 스키마 정의
# FastAPI에서 파일과 폼 데이터를 함께 받으려면 Pydantic 모델만으로는 어렵고,
# 라우터 함수에서 UploadFile과 Form(...)을 함께 사용해야 합니다.
# 따라서 이 Request 스키마는 파일 자체는 포함하지 않고, 파일과 함께 전송될 추가 데이터를 정의합니다.
class NoseProcessRequest(BaseModel):
    # 신규 등록 시 강아지 정보 (선택 사항)
    # 기존 강아지 비문인지 확인하는 경우 이 필드는 비워둘 수 있습니다.
    dog_name: Optional[str] = Field(None, description="신규 등록 시 강아지 이름")
    dog_breed: Optional[str] = Field(None, description="신규 등록 시 강아지 품종")
    # 필요한 경우 강아지의 다른 정보 추가 가능

# 응답 시 포함될 강아지 정보 스키마 (models/user.py 및 models/nose.py 기반)
# User 모델과 NoseVector 모델의 필드를 반영하여 필요한 정보만 포함
class UserSchemaForNose(BaseModel):
    id: int = Field(..., description="사용자 고유 ID")
    username: str = Field(..., description="사용자 이름")
    # email 등 필요한 사용자 정보 추가 가능

    model_config = ConfigDict(from_attributes=True) # SQLAlchemy 모델 호환

class NoseVectorSchema(BaseModel):
    id: int = Field(..., description="비문 벡터 고유 ID")
    class_id: str = Field(..., description="비문 클래스 ID (강아지 식별자)")
    # vector 필드는 크기가 클 수 있고 응답에 필요 없을 수 있으므로 제외
    # created_at 등 필요한 NoseVector 정보 추가 가능

    model_config = ConfigDict(from_attributes=True) # SQLAlchemy 모델 호환

# 비문 처리 응답 스키마
class NoseProcessResponse(BaseModel):
    success: bool = Field(..., description="처리 성공 여부")
    message: str = Field(..., description="처리 결과 메시지")
    is_registered_dog: bool = Field(..., description="기존 등록된 강아지와 일치하는지 여부 (True: 일치, False: 신규/미일치)")
    similarity_score: float = Field(..., description="가장 높은 코사인 유사도 점수")
    # case1: cos_sim > 임계값 -> 기존 강아지 정보 반환
    matched_nose_vector: Optional[NoseVectorSchema] = Field(None, description="기존 등록된 강아지와 일치하는 경우 해당 비문 벡터 정보")
    # matched_user: Optional[UserSchemaForNose] = Field(None, description="일치하는 강아지 소유 사용자 정보 (필요 시 추가)") # User 정보도 필요하면 추가

    # case2: cos_sim < 임계값 -> 신규 강아지 비문으로 처리, 등록된 경우 정보 반환
    newly_registered_nose_vector: Optional[NoseVectorSchema] = Field(None, description="신규 강아지로 등록된 경우 해당 비문 벡터 정보")
    # newly_registered_user: Optional[UserSchemaForNose] = Field(None, description="신규 등록된 강아지 소유 사용자 정보 (필요 시 추가)") # User 정보도 필요하면 추가

    # 여러 개의 유사 비문이 나온 경우 목록 형태로 반환 (선택 사항)
    # similar_noses: Optional[List[NoseVectorSchema]] = Field(None, description="유사도가 높은 비문 목록 (debug/정보 제공용)")