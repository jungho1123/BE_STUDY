# scripts/create_admin_user.py
from app.core.security import hash_password
from app.models.user import User
from app.database.session import SessionLocal

def create_admin():
    db = SessionLocal()
    username = "admin"
    email = "snsdl1123@naver.com"  # 이메일 추가
    password = "fkcmfl12"

    user = User(
        username=username,
        email=email,                     # 여기 추가
        hashed_password=hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"[INFO] 관리자 계정 생성 완료. user_id = {user.user_id}")
    db.close()

if __name__ == "__main__":
    create_admin()
