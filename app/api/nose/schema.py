# app/api/nose/schema.py
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

# Request Body에 포함될 수 있는 추가 데이터 (예: 신규 등록 시 강아지 정보)
# 이미지 파일 자체는 이 스키마에 포함되지 않으며, 라우터에서 UploadFile로 처리됩니다.
class NoseProcessRequest(BaseModel):
    """
    비문 처리 요청 시 이미지 파일과 함께 전달될 추가 정보 스키마.
    신규 등록 가능성이 있는 경우 강아지 정보를 포함합니다.
    """
    # 신규 등록 시 사용될 강아지 이름 (선택 사항)
    dog_name: Optional[str] = Field(None, description="신규 등록 시 강아지 이름")
    # 신규 등록 시 사용될 강아지 품종 (선택 사항)
    dog_breed: Optional[str] = Field(None, description="신규 등록 시 강아지 품종")
    # 추후 필요에 따라 강아지의 다른 정보 필드를 추가할 수 있습니다.

# 응답에 포함될 사용자 정보 스키마 (필요시 사용)
# User 모델 (user.py) 기반으로 응답에 필요한 정보만 노출합니다.
class UserSchemaForNose(BaseModel):
    # User 모델의 user_id (DB 컬럼명 id)에 해당합니다.
    user_id: int = Field(..., description="사용자 고유 ID")
    username: str = Field(..., description="사용자 이름")
    # email 등 다른 사용자 정보가 응답에 필요하다면 추가

    # from_attributes=True를 통해 모델의 user_id 필드와 스키마의 user_id 필드를 매핑합니다.
    model_config = ConfigDict(from_attributes=True)

# 응답에 포함될 비문 벡터 정보 스키마
# NoseVector 모델 (nose.py) 기반으로 응답에 필요한 정보만 노출합니다.
class NoseVectorSchema(BaseModel):
    # NoseVector 모델의 nose_vector_record_id (DB 컬럼명 id)에 해당합니다.
    nose_vector_record_id: int = Field(..., description="비문 벡터 레코드의 고유 ID (DB 기본 키)")
    # NoseVector 모델의 dog_non_print_identifier (DB 컬럼명 class_id)에 해당합니다.
    dog_non_print_identifier: str = Field(..., description="이 비문 벡터가 속한 강아지/비문을 식별하는 논리적 ID")
    # NoseVector 모델의 associated_user_id (DB 컬럼명 user_id)에 해당합니다.
    # associated_user_id: int = Field(..., description="이 비문 벡터 레코드가 연결된 사용자 고유 ID") # 응답에 user ID를 포함할 필요가 없다면 주석 처리
    # vector 필드는 데이터 크기가 크고 응답에 불필요하므로 포함하지 않습니다.
    # created_at 등 필요한 NoseVector 정보 추가 가능

    # from_attributes=True를 통해 모델의 필드와 스키마의 필드를 매핑합니다.
    model_config = ConfigDict(from_attributes=True)

# 비문 처리 결과 응답 스키마 (Case 1, Case 2 모두 포괄)
class NoseProcessResponse(BaseModel):
    """
    비문 처리 API의 응답 데이터 구조 스키마.
    비문 일치 여부, 유사도 점수, 결과 메시지 및 관련 정보를 포함합니다.
    """
    success: bool = Field(..., description="API 요청 처리 성공 여부")
    message: str = Field(..., description="비문 처리 결과에 대한 설명 메시지")
    is_registered_dog: bool = Field(..., description="업로드된 비문이 기존 등록된 강아지와 일치하는지 여부 (True: 일치, False: 신규/미일치)")
    similarity_score: float = Field(..., description="가장 높은 코사인 유사도 점수")

    # Case 1 (is_registered_dog=True) 일 때 제공되는 정보
    # 일치하는 비문 벡터 레코드 정보 (어떤 dog_non_print_identifier와 일치했는지 등)
    # 모델의 NoseVector 객체가 오면 from_attributes=True를 통해 매핑됩니다.
    matched_nose_vector: Optional[NoseVectorSchema] = Field(None, description="기존 등록된 강아지와 일치하는 경우 해당 비문 벡터 레코드 정보")
    # 일치하는 강아지 소유 사용자 정보 (필요하다면 추가)
    # matched_user: Optional[UserSchemaForNose] = Field(None, description="일치하는 강아지 소유 사용자 정보 (필요 시 추가)")

    # Case 2 (is_registered_dog=False) 일 때 제공되는 정보
    # 신규 강아지로 등록된 경우, 새로 생성된 비문 벡터 레코드 정보
    # 모델의 새로 생성된 NoseVector 객체가 오면 from_attributes=True를 통해 매핑됩니다.
    newly_registered_nose_vector: Optional[NoseVectorSchema] = Field(None, description="신규 강아지로 등록된 경우 해당 비문 벡터 레코드 정보")
     # 신규 등록된 강아지 소유 사용자 정보 (필요하다면 추가)
    # newly_registered_user: Optional[UserSchemaForNose] = Field(None, description="신규 등록된 강아지 소유 사용자 정보 (필요 시 추가)")

    # 추후 여러 유사 비문이 나온 경우 목록 형태로 반환하는 필드를 추가할 수 있습니다.
    # similar_noses: Optional[List[NoseVectorSchema]] = Field(None, description="유사도가 높은 비문 목록 (디버그/정보 제공용)")