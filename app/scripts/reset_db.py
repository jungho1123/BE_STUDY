# app/scripts/reset_db.py
import os
import sys

# 스크립트가 app 디렉토리 내부의 모듈을 임포트할 수 있도록 프로젝트 루트를 sys.path에 추가
# 스크립트를 프로젝트 루트 디렉토리에서 실행한다고 가정합니다.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sqlalchemy import create_engine

# 설정 객체 임포트
from app.core.config import settings

# Base 메타데이터 임포트
# app/database/base.py 파일에 Base = declarative_base() 가 정의되어 있어야 합니다.
from app.database.base import Base

# 모델 파일 임포트 (중요! Base.metadata 에 모든 모델이 등록되도록 임포트해야 합니다.)
# 여러분의 모든 SQLAlchemy 모델 파일을 여기에 임포트해야 합니다.
from app.models.user import User
from app.models.nose import NoseVector
# TODO: 다른 모든 모델 파일 (예: app.models.dog, app.models.eye 등) 도 여기에 임포트해야 합니다.
# from app.models.dog import Dog
from app import models

def reset_database():
    """
    데이터베이스에 연결하여 Base.metadata에 정의된 모든 테이블을 삭제(Drop)합니다.
    마이그레이션 워크플로우에서는 테이블 생성(create_all)을 여기서 하지 않고 Alembic으로 수행합니다.
    """
    print("데이터베이스 초기화 시작...")
    try:
        # 설정에서 DATABASE_URL을 가져와 SQLAlchemy 엔진 생성
        engine = create_engine(settings.DATABASE_URL)

        # Base.metadata 에 등록된 모든 테이블을 데이터베이스에서 삭제합니다.
        # 위에서 모든 모델 파일을 임포트했기 때문에, 해당 모델에 대응되는 테이블들이 모두 삭제됩니다.
        print("모든 테이블 삭제 중...")
        Base.metadata.drop_all(bind=engine)
        print("모든 테이블 삭제 완료.")

        # 마이그레이션 워크플로우에서는 테이블 생성을 Alembic으로 수행하므로
        # Base.metadata.create_all() 은 여기서 호출하지 않습니다.
        # 만약 마이그레이션을 사용하지 않고 초기 테이블을 만들고 싶다면 아래 주석을 해제합니다.
        # print("모든 테이블 생성 중...")
        # Base.metadata.create_all(bind=engine)
        # print("모든 테이블 생성 완료.")

        print("데이터베이스 초기화 완료. 테이블이 삭제되었습니다.")
        print("'alembic upgrade head' 명령어를 실행하여 마이그레이션으로 테이블을 다시 생성하세요.")

    except Exception as e:
        print(f"데이터베이스 초기화 중 오류 발생: {e}")
        # 오류 발생 시 스크립트 종료
        sys.exit(1)

# 스크립트를 직접 실행했을 때 reset_database 함수가 호출되도록 합니다.
if __name__ == "__main__":
    reset_database()