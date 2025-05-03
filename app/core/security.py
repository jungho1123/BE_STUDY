from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import timedelta
from app.core.time import get_kst_now
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends
from app.database.session import get_db
from app.models.user import User
from sqlalchemy.orm import Session
# 암호화 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
# FastAPI가 요청 헤더의 "Authorization: Bearer <token>" 형식에서 토큰을 꺼내줌.
# /auth/login은 로그인 시 사용하는 token 발급 API의 경로

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = get_kst_now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str): #JWT 토큰을 디코딩하여 payload(dict) 반환
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
#get_current_user 이 함수는 인증이 필요한 API에서 Depends()로 사용됨
#클라이언트가 보낸 JWT 토큰을 바탕으로 해당 유저 정보를 DB에서 조회해줌
#JWT payload 안에는 우리가 access_token 생성 시 넣은 sub(주체, user_id 또는 username)이 있어야 함
#없으면 유효하지 않은 토큰으로 판단
#토큰에 들어 있던 user_id로 DB에서 실제 유저를 조회
#없으면 탈퇴했거나 잘못된 ID이므로 에러 발생