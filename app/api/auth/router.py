from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from app.core.security import hash_password,verify_password, create_access_token
from app.api.auth import schema
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.core.security import get_current_user

router=APIRouter(prefix="/auth",tags=["Auth"])

@router.post("/signup")
def signup(req:schema.UserSignupRequest,db: Session=Depends(get_db)):
    existing_user=db.query(User).filter(User.username==req.username).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="이미 존재하는 사용자입니다.")
    hashed_pw=hash_password(req.password)
    new_user=User(username=req.username,hash_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "회원가입이 완료되었습니다."}
        
    
@router.post("/login")
def login(req:schema.UserLoginRequest,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.username==req.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="유효하지 않은 사용자입니다.")
    if not verify_password(req.password,user.hashed_password):
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")
    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
            
@router.get("/me")
def get_my_info(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username}
