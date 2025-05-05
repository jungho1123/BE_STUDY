# app/api/nose/service.py
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status

# 모델 임포트 (수정된 변수명 반영)
from app.models.user import User # 현재 사용자의 user_id를 얻기 위해 필요
from app.models.nose import NoseVector # 비문 벡터 레코드와 상호작용

# 스키마 임포트 (응답 데이터 구조 정의)
from app.api.nose.schema import NoseProcessResponse, NoseVectorSchema # UserSchemaForNose는 이 서비스 함수에서 직접 사용되진 않음

# 설정 임포트 (비문 유사도 임계값 등)
from app.core.config import settings # settings 객체가 app.core.config에 정의되어 있다고 가정

# UUID 임포트 (신규 비문 식별자 생성을 위해)
import uuid

# 비문 벡터 처리 관련 유틸리티 함수 임포트 (우리가 작성한 app/utils/vector_processor.py 파일)
# 이 파일에는 extract_nose_vector와 calculate_cosine_similarity 함수의 실제 또는 Placeholder 구현이 있습니다.
from app.utils.vector_processor import extract_nose_vector, calculate_cosine_similarity


# --- DB 상호작용 Private 함수 (모델 상호작용 로직 분리) ---
# 이 함수들은 NoseVector 모델에 대한 CRUD(조회, 생성) 작업을 수행합니다.

def _get_all_nose_vectors(db: Session) -> List[NoseVector]:
    """
    Private 함수: 데이터베이스에서 모든 NoseVector 레코드를 조회합니다.
    (향후 대규모 데이터 시 성능 최적화 필요)
    """
    print("Service(DB): Fetching all nose vectors...")
    # SQLAlchemy 세션을 사용하여 NoseVector 모델의 모든 레코드를 가져옵니다.
    return db.query(NoseVector).all()

# 특정 식별자로 NoseVector 조회하는 함수도 필요하다면 추가할 수 있습니다.
# def _get_nose_vector_by_identifier(db: Session, identifier: str) -> Optional[NoseVector]:
#     print(f"Service(DB): Fetching nose vector with identifier {identifier}...")
#     return db.query(NoseVector).filter(NoseVector.dog_non_print_identifier == identifier).first()


def _create_new_nose_vector(
    db: Session,
    dog_non_print_identifier: str,
    associated_user_id: int,
    feature_vector: List[float]
) -> NoseVector:
    """
    Private 함수: 새로운 NoseVector 레코드를 생성하고 DB에 저장(commit)합니다.
    저장 과정에서 발생하는 DB 오류를 처리하고 롤백합니다.
    """
    print(f"Service(DB): Creating new nose vector for identifier {dog_non_print_identifier}...")
    try:
        # 새로운 NoseVector 모델 객체 생성 (수정된 모델 필드명 사용)
        new_nose_vector_obj = NoseVector(
            dog_non_print_identifier=dog_non_print_identifier, # 생성한 고유 식별자
            associated_user_id=associated_user_id, # 현재 로그인된 사용자의 user_id
            feature_vector=feature_vector # 추출된 비문 벡터
            # created_at 필드는 모델 기본값 사용
        )
        # 세션에 객체 추가
        db.add(new_nose_vector_obj)
        # DB에 변경사항 커밋
        db.commit()
        # DB에서 할당된 nose_vector_record_id 등을 가져오기 위해 객체 새로고침
        db.refresh(new_nose_vector_obj)
        print(f"Service(DB): Successfully created nose vector record with ID {new_nose_vector_obj.nose_vector_record_id}")
        # 새로 생성된 모델 객체 반환
        return new_nose_vector_obj
    except Exception as e:
        # DB 오류 발생 시 롤백
        db.rollback()
        print(f"Service(DB Error): Failed to create new nose vector: {e}") # 에러 로깅
        # DB 오류를 다시 발생시켜 호출하는 상위 함수(process_nose_image)에서 잡도록 함
        raise e

# 필요에 따라 DB 삭제(_delete_nose_vector) 등 다른 DB 상호작용 함수 추가


# --- 메인 서비스 함수 (전체 비문 처리 흐름 제어) ---
# 이 함수는 app/api/nose/router.py에서 호출됩니다.
async def process_nose_image(
    db: Session, # 라우터에서 Depends(get_db)로 주입받은 DB 세션
    image_file: UploadFile, # 라우터에서 File(...)로 받은 업로드 파일
    current_user: User, # 라우터에서 Depends(get_current_user)로 주입받은 User 객체
    dog_name: Optional[str] = None, # 라우터에서 Form(...)으로 받은 강아지 이름 (선택 사항)
    dog_breed: Optional[str] = None # 라우터에서 Form(...)으로 받은 강아지 품종 (선택 사항)
) -> NoseProcessResponse: # NoseProcessResponse 스키마 객체를 반환
    """
    비문 이미지를 처리하고 DB에 등록된 비문과 비교하거나 신규 등록하는 서비스 로직.

    Args:
        db: SQLAlchemy DB 세션 객체.
        image_file: 업로드된 비문 이미지 파일.
        current_user: 현재 인증된 User 모델 객체. user_id 필드를 가집니다.
        dog_name: 신규 등록 시 강아지 이름 (선택 사항).
        dog_breed: 신규 등록 시 강아지 품종 (선택 사항).

    Returns:
        NoseProcessResponse 스키마에 따른 처리 결과.
    """
    print(f"Service: Starting nose image processing for user {current_user.user_id}...")

    # 서비스 함수 전체에서 발생할 수 있는 예외를 처리하고 응답 형식을 맞추기 위한 try 블록
    try:
        # 1. 업로드된 이미지 파일 내용 비동기적으로 읽기
        # await 키워드는 I/O 작업이 완료될 때까지 기다리지만 이벤트 루프를 블록하지 않습니다.
        print("Service: Reading image file...")
        image_bytes = await image_file.read()
        print("Service: Image file read complete.")

        # 2. 이미지 바이트에서 비문 특징 벡터 추출 (util 함수 호출)
        # extract_nose_vector 함수 내부에 실제 ML 모델 추론 코드가 있습니다.
        # 이 함수는 비동기일 수 있습니다 (async def).
        print("Service: Calling vector extraction utility...")
        extracted_vector = await extract_nose_vector(image_bytes) # await 필요 여부는 extract_nose_vector 정의에 따름
        print(f"Service: Vector extraction returned: {'Success' if extracted_vector is not None else 'Failure'}")


        if extracted_vector is None:
            # 벡터 추출 실패 시, 오류 응답 스키마 반환
            return NoseProcessResponse(
                success=False,
                message="비문 특징 벡터 추출에 실패했습니다. 이미지를 확인해주세요.",
                is_registered_dog=False,
                similarity_score=0.0,
                matched_nose_vector=None,
                newly_registered_nose_vector=None
            )

        # 3. 데이터베이스에서 모든 기존 비문 벡터 레코드 조회 (Private DB 함수 호출)
        print("Service: Calling DB utility to get all nose vectors...")
        all_nose_vectors = _get_all_nose_vectors(db)
        print(f"Service: Found {len(all_nose_vectors)} existing nose vectors in DB.")


        best_match: Optional[NoseVector] = None # 가장 유사한 NoseVector 객체 저장
        highest_similarity = 0.0 # 가장 높은 유사도 점수

        # 4. 추출된 벡터와 DB 벡터들 간 코사인 유사도 계산 및 베스트 매치 찾기
        # 이 부분은 벡터가 많아지면 성능 병목이 됩니다. (향후 개선 필요)
        print("Service: Calculating similarities with existing vectors...")
        for db_vector_obj in all_nose_vectors:
            # DB에 저장된 feature_vector (JSON -> List)와 추출된 벡터 간 유사도 계산
            similarity = calculate_cosine_similarity(extracted_vector, db_vector_obj.feature_vector)

            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = db_vector_obj
        print(f"Service: Highest similarity found: {highest_similarity:.2f}")


        # 5. 설정된 임계값과 비교하여 Case 1 (기존 비문) 또는 Case 2 (신규 비문) 판단
        threshold = settings.NOSE_SIMILARITY_THRESHOLD # config.py에서 정의된 임계값

        if highest_similarity > threshold and best_match:
            # Case 1: 추출된 비문이 기존 등록된 강아지의 비문과 일치합니다.
            print(f"Service: Case 1 - Matched existing dog (Identifier: {best_match.dog_non_print_identifier}).")

            # DB에서 가져온 모델 객체 (best_match)의 정보를 스키마로 변환하여 응답에 포함
            matched_nose_schema = NoseVectorSchema.model_validate(best_match)

            return NoseProcessResponse(
                success=True, # 처리 성공
                message=f"기존에 등록된 강아지의 비문과 일치합니다 (유사도: {highest_similarity:.2f}).",
                is_registered_dog=True, # 기존 강아지 맞음
                similarity_score=highest_similarity,
                matched_nose_vector=matched_nose_schema, # 일치하는 비문 정보
                newly_registered_nose_vector=None # 신규 등록이 아니므로 None
                # 필요하다면 일치하는 강아지/사용자 추가 정보 포함 가능
            )
        else:
            # Case 2: 추출된 비문이 기존 등록된 강아지와 일치하지 않습니다. 신규 비문으로 판단하고 등록합니다.
            print(f"Service: Case 2 - No significant match found (Highest similarity: {highest_similarity:.2f}). Registering as new...")

            # 6. 신규 비문 등록 과정 시작

            # 6a. 신규 비문을 위한 고유 식별자 생성 (UUID 사용)
            new_dog_identifier = str(uuid.uuid4())
            print(f"Service: Generated new identifier: {new_dog_identifier}")

            # 6b. 새로운 NoseVector 레코드를 생성하고 DB에 저장 (Private DB 함수 호출)
            # _create_new_nose_vector 함수 내에서 DB commit/rollback이 처리됩니다.
            # 이 함수 호출 중 DB 오류가 발생하면 예외가 다시 발생합니다 (raise e)
            try:
                new_nose_vector_obj = _create_new_nose_vector(
                    db=db, # DB 세션 전달
                    dog_non_print_identifier=new_dog_identifier, # 생성한 고유 식별자
                    associated_user_id=current_user.user_id,     # 현재 로그인된 사용자의 user_id (User 모델에서 가져옴)
                    feature_vector=extracted_vector              # 추출된 비문 벡터
                )
                print(f"Service: Successfully created new nose vector record with ID {new_nose_vector_obj.nose_vector_record_id}")

                # 7. 신규 등록 성공 응답 구성
                # 새로 생성된 모델 객체 (DB에서 새로고침된)의 정보를 스키마로 변환하여 응답에 포함
                newly_registered_schema = NoseVectorSchema.model_validate(new_nose_vector_obj)

                return NoseProcessResponse(
                    success=True, # 처리 성공 (등록 성공)
                    message=f"신규 강아지의 비문입니다. DB에 성공적으로 등록되었습니다 (식별자: {new_dog_identifier}).",
                    is_registered_dog=False, # 기존 강아지 아님
                    similarity_score=highest_similarity, # 신규이므로 이 값은 임계값 이하일 것임
                    matched_nose_vector=None, # 일치하는 비문 없음
                    newly_registered_nose_vector=newly_registered_schema # 새로 등록된 비문 정보
                    # 필요하다면 신규 강아지/사용자 추가 정보 포함 (dog_name, dog_breed 활용하여 응답 메시지 등 구성 가능)
                )

            except Exception as db_error:
                 # _create_new_nose_vector 함수에서 발생한 DB 오류를 여기서 잡습니다.
                 # _create_new_nose_vector 내에서 이미 rollback 되었으므로 여기서 추가 rollback은 필요 없습니다.
                 print(f"Service(Error): Caught DB error during new nose vector creation: {db_error}") # 로깅

                 # DB 오류 응답 구성
                 return NoseProcessResponse(
                     success=False, # 처리 실패 (DB 저장 실패)
                     message=f"신규 비문 등록 중 DB 오류 발생: {db_error}",
                     is_registered_dog=False,
                     similarity_score=0.0, # 오류 시 유사도 의미 없음
                     matched_nose_vector=None,
                     newly_registered_nose_vector=None
                 )


    except Exception as general_error:
        # 이미지 파일 읽기, 벡터 추출 유틸 함수 호출 중 발생한 오류 등
        # DB 트랜잭션이 시작되기 전에 발생한 오류일 수 있습니다.
        # _create_new_nose_vector 호출 이전에 발생한 오류라면 db.rollback()이 필요합니다.
        # Depends(get_db)는 요청별 세션을 제공하지만, 명시적 commit/rollback 없이는 기본적으로 auto-commit 되지 않습니다.
        # 따라서 안전하게 여기서도 rollback을 호출합니다.
        db.rollback() # 오류 발생 시 DB 세션 상태를 정리

        print(f"Service(Error): Caught general error during nose image processing: {general_error}") # 로깅

        # 일반 처리 오류 응답 구성
        return NoseProcessResponse(
            success=False, # 처리 실패
            message=f"비문 처리 중 오류 발생: {general_error}",
            is_registered_dog=False,
            similarity_score=0.0, # 오류 시 유사도 의미 없음
            matched_nose_vector=None,
            newly_registered_nose_vector=None
        )

# 필요에 따라 비문 관련 다른 서비스 함수들을 여기에 추가합니다.
# 예:
# def get_user_nose_vectors(db: Session, user_id: int) -> List[NoseVector]:
#     """특정 사용자의 모든 비문 벡터 레코드 조회"""
#     # db.query(NoseVector).filter(NoseVector.associated_user_id == user_id).all()
#     pass
#
# def delete_nose_vector(db: Session, vector_record_id: int, user_id: int) -> bool:
#     """특정 비문 벡터 레코드 삭제 (소유자 확인 포함)"""
#     # item = db.query(NoseVector).filter(NoseVector.nose_vector_record_id == vector_record_id, NoseVector.associated_user_id == user_id).first()
#     # if item:
#     #     db.delete(item)
#     #     db.commit()
#     #     return True
#     # return False
#     pass