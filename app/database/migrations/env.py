# app/database/migrations/env.py
import sys
import os
sys.stderr.write("--- env.py start (very first line to stderr) ---\n")
print("--- env.py start (very first line to stdout) ---")
from logging.config import fileConfig
import logging # 로깅 설정에 사용

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.orm import Session as al_Session # Alembic 내부에서 Session을 사용할 경우 충돌 방지
# from sqlalchemy.orm import configure_mappers # 필요시 사용할 수 있음

from alembic import context

# Alembic 로거 설정 (디버그 출력을 확인하기 위해 INFO 레벨로 설정)
logger = logging.getLogger(__name__)
logger.configure_from_file = fileConfig
logger.setLevel(logging.INFO)


# --- 프로젝트 루트 경로를 sys.path에 추가 ---
# alembic 명령어를 프로젝트 루트 디렉토리에서 실행한다고 가정합니다.
# 이 설정이 여러분의 환경에서 올바른 경로를 가리키는지 확인해야 합니다.
print(f"env.py: 현재 작업 디렉토리: {os.getcwd()}") # 현재 alembic 명령을 실행한 디렉토리 출력
script_dir = os.path.dirname(__file__) # env.py 파일이 있는 디렉토리 (예: app/database/migrations)
# env.py 로부터 프로젝트 루트까지의 상대 경로를 계산합니다.
# 예: app/database/migrations -> ../ (database) -> ../ (app) -> ../ (프로젝트 루트)
project_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
sys.path.insert(0, project_root) # 계산된 프로젝트 루트 경로를 sys.path 맨 앞에 추가
print(f"env.py: {project_root} 경로를 sys.path 에 추가했습니다.")
print(f"env.py: 현재 sys.path: {sys.path}") # 현재 sys.path 내용 출력


# --- 여러분의 애플리케이션 설정 및 모델 임포트 ---
# **이 부분의 임포트들이 중요합니다. 임포트 성공/실패를 확인해야 합니다.**

# settings 임포트 시도 및 결과 출력
try:
    # from app.core.config import settings # 설정 객체 임포트
    # 임포트 오류 시 sys.path 문제일 가능성이 높습니다.
    from app.core.config import settings
    print("env.py: settings 모듈 임포트 성공.")
except ImportError as e:
    print(f"env.py 오류: settings 모듈 임포트 실패 - {e}") # 임포트 실패 시 오류 출력
    logger.error(f"Failed to import settings: {e}") # 로거에도 기록
    # 설정 없이는 진행 불가하므로 종료할 수도 있습니다. sys.exit(1)

# Base 임포트 시도 및 결과 출력
try:
    # from app.database.base import Base # Base 객체 임포트
    # Base = declarative_base() 가 정의된 파일입니다.
    # 임포트 오류 시 sys.path 또는 파일 경로 문제일 수 있습니다.
    from app.database.base import Base
    print("env.py: Base 모듈 임포트 성공.")
    # NOTE: 이 시점에는 Base.metadata.tables 가 비어 있을 수 있습니다.
    #       Base 를 상속받는 모델들이 아직 임포트되거나 정의되지 않았기 때문입니다.
    # print(f"env.py: Base.metadata.tables (Base 임포트 직후): {Base.metadata.tables}")
except ImportError as e:
    print(f"env.py 오류: Base 모듈 임포트 실패 - {e}") # 임포트 실패 시 오류 출력
    logger.error(f"Failed to import Base: {e}") # 로거에도 기록
     # Base 없이는 진행 불가하므로 종료할 수도 있습니다. sys.exit(1)


# ** Base 를 상속받는 모든 모델 클래스 파일** 을 여기에 임포트해야 합니다.
# ** 이 임포트들이 오류 없이 실행되어야 Base.metadata 에 모델 정보가 채워집니다. **
# ** 각 모델 파일의 실제 위치에 맞춰 임포트 경로를 정확하게 수정해야 합니다. **

print("env.py: 모델 파일 임포트를 시작합니다.")
# 각 모델 임포트 시도 및 결과 출력 (try...except 블록 필수)
try:
    # from app.models.user import User # User 모델 임포트
    from app.models.user import User
    print("env.py: User 모델 임포트 성공.")
except ImportError as e:
    print(f"env.py 오류: User 모델 임포트 실패 - {e}")
    logger.warning(f"Failed to import User model: {e}") # 이 모델 없이는 테이블 생성 불가

try:
    # from app.models.nose import NoseVector # NoseVector 모델 임포트
    from app.models.nose import NoseVector
    print("env.py: NoseVector 모델 임포트 성공.")
except ImportError as e:
    print(f"env.py 오류: NoseVector 모델 임포트 실패 - {e}")
    logger.warning(f"Failed to import NoseVector model: {e}") # 이 모델 없이는 테이블 생성 불가

# TODO: 여러분의 프로젝트에 있는 다른 모든 모델 파일 (Base 상속 모델) 도 여기에 임포트했는지 다시 확인하고,
#       각 임포트마다 try...except 블록과 print 문을 추가하여 임포트 성공/실패를 확인하세요.
#       모델 파일의 실제 위치와 이름에 맞춰 임포트 경로를 수정해야 합니다.
#       예시:
# try:
#     from app.models.dog_post import DogPost
#     print("env.py: DogPost 모델 임포트 성공.")
# except ImportError as e:
#     print(f"env.py 오류: DogPost 모델 임포트 실패 - {e}")
#     logger.warning(f"Failed to import DogPost model: {e}")

# 예시: 만약 models 디렉토리 아래 하위 디렉토리에 모델이 있다면:
# try:
#     from app.models.some_domain.model_file import YourModel
#     print("env.py: YourModel 모델 임포트 성공.")
# except ImportError as e:
#     print(f"env.py 오류: YourModel 모델 임포트 실패 - {e}")
#     logger.warning(f"Failed to import YourModel model: {e}")

# configure_mappers() 는 모든 모델이 임포트된 후에 호출될 수 있습니다 (선택 사항)
# configure_mappers()


# this is the Alembic Config object, which provides
# access to values within the .ini file in this revision context.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers based on the logging section in alembic.ini.
# fileConfig(config.config_file_name) # 이미 위에 설정했거나 필요시 여기서 다시 설정

# provide our SQLAlchemy declarative base metadata object to Alembic.
# target_metadata 는 임포트된 모든 모델의 테이블 정보를 담고 있어야 합니다.
target_metadata = Base.metadata # <-- 이 라인이 있는지 확인합니다.
# **이 라인이 실행된 후 Base.metadata.tables 에 임포트된 모델들의 테이블 정보가 채워져 있어야 합니다.**
print(f"env.py: Base.metadata.tables (모델 임포트 모두 완료 후): {Base.metadata.tables}") # <-- 여기에 테이블 목록이 출력되는지 확인!
sys.stderr.write("env.py: Base.metadata.tables after imports (to stderr): " + str(Base.metadata.tables) + "\n") # <-- stderr로 출력 추가

# ... (나머지 코드) ...

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a database to help us.

    Keyword arguments can be passed
    to the compare migrations set of hooks via the object
    passed to context.configure().
    """
    # --- 데이터베이스 URL 설정 (오프라인 모드) ---
    # alembic.ini 의 sqlalchemy.url 대신 settings 객체에서 DATABASE_URL 을 가져옵니다.
    # settings 객체가 임포트 실패했다면 이 부분에서 오류가 발생할 수 있습니다.
    try:
        url = settings.DATABASE_URL
        print(f"env.py: 오프라인 모드 - DB URL 설정: {url}")
    except Exception as e:
         print(f"env.py 오류: 오프라인 모드 DB URL 설정 실패 - {e}")
         logger.error(f"Failed to get DB URL for offline mode: {e}")
         url = None # URL 없으면 마이그레이션 불가

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # compare_type=True # 데이터 타입 변경 감지 활성화 (필요시 주석 해제)
        # version_table_schema=target_metadata.schema # 스키마 사용시 필요
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # --- 데이터베이스 URL 설정 (온라인 모드) ---
    # alembic.ini 에서 설정 섹션을 가져와 sqlalchemy.url 을 settings.DATABASE_URL 로 덮어씁니다.
    # settings 객체가 임포트 실패했다면 이 부분에서 오류가 발생할 수 있습니다.
    try:
        configuration = config.get_section(config.config_ini_section)
        configuration["sqlalchemy.url"] = settings.DATABASE_URL # <-- settings 에서 URL 가져와 설정
        print(f"env.py: 온라인 모드 - DB URL 설정: {configuration['sqlalchemy.url']}")
    except Exception as e:
         print(f"env.py 오류: 온라인 모드 DB URL 설정 실패 - {e}")
         logger.error(f"Failed to get DB URL for online mode: {e}")
         # URL 없으면 엔진 생성 불가
         return


    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool, # 마이그레이션 시에는 커넥션 풀 필요 없음
    )

    with connectable.connect() as connection:
        # Alembic 컨텍스트 설정
        context.configure(
            connection=connection, # DB 연결 정보 전달
            target_metadata=target_metadata, # 마이그레이션 대상 스키마 정보 전달
            # compare_type=True # 데이터 타입 변경 감지 활성화 (필요시 주석 해제)
            # version_table_schema=target_metadata.schema # 스키마 사용시 필요
        )

        with context.begin_transaction():
            context.run_migrations()


# 스크립트 실행 모드에 따라 오프라인/온라인 마이그레이션 실행
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()