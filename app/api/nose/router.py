# app/api/nose/router.py
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

# DB 세션 의존성 주입
from app.database.session import get_db

# 사용자 인증 의존성 주입
from app.core.security import get_current_user
from app.models.user import User # User 모델 임포트 (get_current_user에서 사용)

# 비문 관련 스키마 및 서비스 임포트
from app.api.nose import schema
from app.api.nose import service # 작성한 서비스 파일 임포트

# APIRouter 인스턴스 생성
# prefix="/nose"로 설정하여 이 라우터에 정의된 모든 엔드포인트는 "/nose" 경로 아래에 위치하게 됩니다.
router = APIRouter(
    prefix="/nose",
    tags=["Nose"] # 문서화를 위한 태그
)

# 비문 처리 엔드포인트 정의
@router.post(
    "/process",
    response_model=schema.NoseProcessResponse, # 응답 스키마 지정
    summary="Upload a nose image for processing (check or register)" # 문서화 요약
)
async def process_nose_image_endpoint(
    # 이미지 파일 업로드 (Required)
    image_file: UploadFile = File(..., description="Upload the dog's nose image file"),

    # Request Body의 JSON 데이터 대신 Form 데이터로 추가 정보 받기
    # 파일과 함께 다른 필드를 보내려면 Form을 사용해야 합니다.
    dog_name: Optional[str] = Form(None, description="Dog's name (optional, for new registration)"),
    dog_breed: Optional[str] = Form(None, description="Dog's breed (optional, for new registration)"),
    # 필요에 따라 다른 폼 필드 추가

    # DB 세션 의존성 주입
    db: Session = Depends(get_db),

    # 현재 인증된 사용자 정보 의존성 주입
    current_user: User = Depends(get_current_user) # get_current_user는 User 모델 객체를 반환한다고 가정
):
    """
    강아지 비문 이미지를 업로드하여 데이터베이스에 등록된 비문과 비교하거나,
    신규 강아지 비문으로 등록합니다.

    - 이미지를 업로드합니다.
    - 인증된 사용자만 접근 가능합니다.
    - 이미지에서 특징 벡터를 추출합니다.
    - 기존 DB의 비문 벡터와 유사도를 계산합니다.
    - 유사도가 임계값 이상이면 기존 강아지로 판단하고 정보를 반환합니다 (Case 1).
    - 유사도가 임계값 미만이거나 일치하는 비문이 없으면 신규 강아지로 판단하고 비문을 등록합니다 (Case 2).
    - 처리 결과와 함께 관련 정보 (일치/신규 비문 정보)를 반환합니다.
    """
    # 서비스 계층의 process_nose_image 함수 호출
    # 필요한 모든 인자(db 세션, 이미지 파일, 현재 사용자, 폼 데이터)를 전달합니다.
    # 서비스 함수가 async 이므로 await 키워드를 사용합니다.
    response_data = await service.process_nose_image(
        db=db,
        image_file=image_file,
        current_user=current_user,
        dog_name=dog_name, # 폼 데이터 전달
        dog_breed=dog_breed # 폼 데이터 전달
    )

    # 서비스 함수가 반환한 응답 스키마 객체를 클라이언트에 반환합니다.
    # FastAPI는 이 객체를 자동으로 JSON으로 직렬화합니다.
    return response_data

# 필요에 따라 비문 관련 다른 라우터 엔드포인트를 여기에 추가합니다.
# 예:
# @router.get("/user/noses", response_model=List[schema.NoseVectorSchema])
# def get_user_noses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     """현재 사용자가 등록한 비문 목록 조회"""
#     # 서비스 함수 호출 (예: service.get_user_noses(db, current_user.user_id))
#     pass

# @router.delete("/vector/{vector_id}", response_model=schema.SuccessResponse) # 가정
# def delete_nose_vector(vector_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     """등록된 비문 데이터 삭제"""
#      # 서비스 함수 호출 (예: service.delete_nose_vector(db, vector_id, current_user.user_id))
#     pass