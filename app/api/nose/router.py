from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import decode_token
from app.database.session import get_db
from app.models.nose import NoseVector
from app.api.nose.schema import NoseVerifyResponse
from app.api.nose.service import extract_feature_vector
from app.api.nose.service import find_most_similar
from fastapi.security import OAuth2PasswordBearer


router=APIRouter()

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")

@router.post("/verify-nose",response_model=NoseVerifyResponse)
def verify_nose(
    image:UploadFile=File(...),
    token:str =Depends(oauth2_scheme),
    db: Session =Depends(get_db),
    
):
    payload=decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401,detail="로그인후 이용가능 합니다.")
    user_id=payload.get("sub")
    
    
    try:
        query_vec=extract_feature_vector(image)
    except Exception:
        raise HTTPException(status_code=400,detail="이미지 처리에 실패했습니다.")
    
    try:
        vectors = db.query(NoseVector).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB에서 벡터 로드 중 오류 발생: {str(e)}")
    
    best_class_id,similarity=find_most_similar(query_vec,vectors)
    
    if similarity>=0.75:
        return NoseVerifyResponse(
            matched=True,
            matched_class_id=best_class_id,
            similarity =similarity,
            message="기존에 등록된 강아지로 확인되었습니다"
        )
    else:
        return NoseVerifyResponse(
            matched=False,
            similarity=similarity,
            message="비문등록이 완료되었습니다."
        )
        