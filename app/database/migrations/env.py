# app/database/migrations/env.py
import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Alembic Config 객체
config = context.config

# 프로젝트 루트 경로를 sys.path에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# 설정과 모델 임포트
from app.core.config import settings
from app.database.base import Base
from app.models import user, post, nose  # 모든 모델 import

# DB URL을 동적으로 설정
config.set_main_option("sqlalchemy.url", settings.database_url)

# metadata 지정
target_metadata = Base.metadata

# 기타 기본 설정 유지
fileConfig(config.config_file_name)

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
