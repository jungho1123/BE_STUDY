# app/api/nose/service.py
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status

# 모델 임포트 (수정된 변수명 반영)
from app.models.user import User
from app.models.nose import NoseVector

# 스키마 임포트
from app.api.nose.schema import NoseProcessResponse, NoseVectorSchema # UserSchemaForNose는 이 예시에서 직접 사용되진 않음

# 설정 임포트 (임계값 등)
from app.core.config import settings # settings 객체가 app.core.config에 정의되어 있다고 가정

# UUID 임포트 (고유 식별자 생성을 위해)
import uuid

# 비문 벡터 처리 관련 유틸리티 함수 임포트 (Placeholder 또는 실제 구현 파일)
# from app.utils.vector_processor import extract_nose_vector, calculate_cosine_similarity

# --- Placeholder: 실제 비문 처리 로직으로 교체 필요 ---
# 이 함수들은 ML 모델 연동 등 계산/처리 로직을 담당하며, DB 상호작용은 하지 않습니다.
async def extract_nose_vector(image_file_content: bytes) -> Optional[List[float]]:
    """
    Placeholder: 비문 이미지 파일 내용에서 특징 벡터를 추출하는 비동기 함수.
    """
    print("Placeholder: Extracting nose vector...")
    import random
    import time
    # await asyncio.sleep(1)
    if random.random() < 0.1:
         print("Placeholder: Vector extraction failed.")
         return None
    dummy_vector = [random.random() for _ in range(512)]
    print("Placeholder: Vector extracted.")
    return dummy_vector

def calculate_cosine_similarity(vector1: List[float], vector2: List[float]) -> float:
    """
    Placeholder: 두 벡터 간의 코사인 유사도를 계산하는 함수.
    """
    # print("Placeholder: Calculating cosine similarity...")
    import random
    return random.uniform(0.0, 1.0)
# --- Placeholder 끝 ---


# --- DB 상호작용 Private 함수 (모델 상호작용 로직 분리 예시) ---

def _get_all_nose_vectors(db: Session) -> List[NoseVector]:
    """
    Private 함수: 데이터베이스에서 모든 NoseVector 레코드를 조회합니다.
    이 함수는 DB 조회(SELECT) 역할만 합니다.
    """
    print("DB: Fetching all nose vectors...")
    # SQLAlchemy 모델 (nose.py에서 수정한 변수명 포함) 사용
    # 여기에 db.query().filter()... 등 조회 로직이 들어갑니다.
    return db.query(NoseVector).all() # 모든 레코드 조회 예시

# 특정 식별자로 NoseVector 조회하는 함수도 추가할 수 있습니다.
# def _get_nose_vector_by_identifier(db: Session, identifier: str) -> Optional[NoseVector]:
#     print(f"DB: Fetching nose vector with identifier {identifier}...")
#     return db.query(NoseVector).filter(NoseVector.dog_non_print_identifier == identifier).first()


def _create_new_nose_vector(
    db: Session,
    dog_non_print_identifier: str,
    associated_user_id: int,
    feature_vector: List[float]
) -> NoseVector:
    """
    Private 함수: 새로운 NoseVector 레코드를 생성하고 DB에 저장합니다.
    이 함수는 DB 삽입(INSERT) 역할과 트랜잭션(commit/rollback)을 관리합니다.
    """
    print(f"DB: Creating new nose vector for identifier {dog_non_print_identifier}...")
    try:
        # 새로운 NoseVector 객체 생성 (수정된 모델 필드명 사용)
        new_nose_vector_obj = NoseVector(
            dog_non_print_identifier=dog_non_print_identifier,
            associated_user_id=associated_user_id, # 현재 로그인된 사용자의 user_id
            feature_vector=feature_vector # 추출된 비문 벡터
        )
        db.add(new_nose_vector_obj)
        db.commit()
        db.refresh(new_nose_vector_obj) # DB에서 할당된 ID 등을 가져옴
        print(f"DB: Successfully created nose vector record with ID {new_nose_vector_obj.nose_vector_record_id}")
        return new_nose_vector_obj
    except Exception as e:
        db.rollback()
        print(f"DB Error during create_new_nose_vector: {e}") # 에러 로깅
        # 여기서는 DB 오류를 다시 발생시키거나 (raise e),
        # 호출하는 쪽에서 오류 처리를 하도록 None 등을 반환할 수 있습니다.
        # 예시에서는 오류를 다시 발생시켜 상위 try 블록에서 잡도록 합니다.
        raise e # DB 오류를 다시 발생시킴

# 필요에 따라 DB 삭제(_delete_nose_vector) 등 다른 DB 상호작용 함수 추가

# --- 메인 서비스 함수 (분리된 Private 함수 호출) ---

async def process_nose_image(
    db: Session, # DB 세션은 여기서 인자로 받습니다.
    image_file: UploadFile,
    current_user: User,
    dog_name: Optional[str] = None,
    dog_breed: Optional[str] = None
) -> NoseProcessResponse:
    """
    비문 이미지를 처리하고 DB에 등록된 비문과 비교하거나 신규 등록하는 서비스 로직.
    이 함수는 전체 흐름을 제어하며, DB 상호작용은 내부 Private 함수에 위임합니다.
    """
    # 이 함수 범위 내에서 발생할 수 있는 일반적인 오류를 처리하는 try 블록
    try:
        # 1. 이미지 파일 내용 비동기적으로 읽기
        image_bytes = await image_file.read()

        # 2. 이미지에서 비문 벡터 추출 (Placeholder 함수 호출)
        extracted_vector = await extract_nose_vector(image_bytes)

        if extracted_vector is None:
            # 벡터 추출 실패 시 처리
            return NoseProcessResponse(
                success=False,
                message="비문 특징 벡터 추출에 실패했습니다. 이미지를 확인해주세요.",
                is_registered_dog=False,
                similarity_score=0.0,
                matched_nose_vector=None,
                newly_registered_nose_vector=None
            )

        # 3. DB에 저장된 모든 비문 벡터 조회 (Private 함수 호출)
        # 직접 db.query(...) 하지 않고, 분리된 함수를 호출합니다.
        all_nose_vectors = _get_all_nose_vectors(db)

        best_match: Optional[NoseVector] = None
        highest_similarity = 0.0

        # 4. 추출된 벡터와 DB 벡터들 간 코사인 유사도 계산 및 베스트 매치 찾기
        # 이 부분은 ML/계산 로직으로, DB 상호작용과는 별개입니다.
        for db_vector_obj in all_nose_vectors:
            db_vector_list = db_vector_obj.feature_vector # 수정된 변수명 사용
            similarity = calculate_cosine_similarity(extracted_vector, db_vector_list)
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = db_vector_obj

        # 5. 임계값과 비교하여 Case 1 또는 Case 2 판단
        threshold = settings.NOSE_SIMILARITY_THRESHOLD

        if highest_similarity > threshold and best_match:
            # Case 1: 기존에 등록된 강아지의 비문입니다.
            matched_nose_schema = NoseVectorSchema.model_validate(best_match)

            return NoseProcessResponse(
                success=True,
                message=f"기존에 등록된 강아지의 비문과 일치합니다 (유사도: {highest_similarity:.2f}).",
                is_registered_dog=True,
                similarity_score=highest_similarity,
                matched_nose_vector=matched_nose_schema,
                newly_registered_nose_vector=None
            )
        else:
            # Case 2: 신규 강아지의 비문입니다. DB에 등록합니다.

            # 6. 신규 비문 등록 과정 시작

            # 6a. 고유 dog_non_print_identifier 생성
            new_dog_identifier = str(uuid.uuid4())

            # 6b. 새로운 NoseVector 레코드를 생성하고 DB에 저장 (Private 함수 호출)
            # DB 저장 로직은 _create_new_nose_vector 함수 내에서 처리됩니다.
            # _create_new_nose_vector에서 오류 발생 시 예외가 다시 발생합니다.
            try:
                new_nose_vector_obj = _create_new_nose_vector(
                    db=db, # DB 세션 전달
                    dog_non_print_identifier=new_dog_identifier,
                    associated_user_id=current_user.user_id,
                    feature_vector=extracted_vector
                )

                # 7. 신규 등록 성공 응답 구성
                newly_registered_schema = NoseVectorSchema.model_validate(new_nose_vector_obj)

                return NoseProcessResponse(
                    success=True,
                    message=f"신규 강아지의 비문입니다. DB에 성공적으로 등록되었습니다 (식별자: {new_dog_identifier}).",
                    is_registered_dog=False,
                    similarity_score=highest_similarity,
                    matched_nose_vector=None,
                    newly_registered_nose_vector=newly_registered_schema
                )

            except Exception as db_error:
                 # _create_new_nose_vector 함수에서 발생한 DB 오류를 여기서 잡습니다.
                 print(f"Caught DB error from _create_new_nose_vector: {db_error}") # 로깅

                 # DB 오류 응답
                 return NoseProcessResponse(
                     success=False,
                     message=f"신규 비문 등록 중 DB 오류 발생: {db_error}",
                     is_registered_dog=False,
                     similarity_score=0.0,
                     matched_nose_vector=None,
                     newly_registered_nose_vector=None
                 )


    except Exception as general_error:
        # 파일 읽기, 벡터 추출 등 _create_new_nose_vector 호출 이전에 발생한 오류 처리
        # 서비스 함수 시작 시 트랜잭션이 시작되었다면 여기서 롤백합니다.
        # get_db Depends는 기본적으로 요청별 세션을 제공하며, 명시적 commit/rollback이 필요합니다.
        # _create_new_nose_vector는 자체 트랜잭션 관리를 하므로 여기서는 그 이전 오류만 고려합니다.
        db.rollback() # 예: 이미지 읽기, 벡터 추출 실패 시

        # 일반 오류 응답
        return NoseProcessResponse(
            success=False,
            message=f"비문 처리 중 오류 발생: {general_error}",
            is_registered_dog=False,
            similarity_score=0.0,
            matched_nose_vector=None,
            newly_registered_nose_vector=None
        )

# 필요에 따라 비문 관련 다른 서비스 함수들을 여기에 추가합니다.