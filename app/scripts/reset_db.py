# scripts/reset_db.py
import os
from app.database.base import Base
from app.database.session import engine

def reset_db():
    print("[INFO] 모든 테이블 삭제 중...")
    Base.metadata.drop_all(bind=engine)
    print("[INFO] 삭제 완료.")

    print("[INFO] 테이블 재생성 중...")
    Base.metadata.create_all(bind=engine)
    print("[INFO] 재생성 완료.")

if __name__ == "__main__":
    reset_db()
