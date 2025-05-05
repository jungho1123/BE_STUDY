# app/core/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr # 민감 정보는 SecretStr로 관리

class Settings(BaseSettings):
    """
    애플리케이션 설정을 관리하는 클래스.
    환경 변수 또는 .env 파일에서 설정을 로드합니다.
    """
    # 프로젝트 기본 설정
    PROJECT_NAME: str = "SIXSENCE" # 프로젝트 이름 기본값
    DEBUG: bool = False # 디버그 모드 기본값 (False 권장)

    # 데이터베이스 설정
    DATABASE_URL: str

    # 보안 설정 (JWT 등)
    SECRET_KEY: SecretStr # 보안을 위해 SecretStr 사용
    ALGORITHM: str = "HS256" # JWT 서명 알고리즘 기본값
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Access Token 만료 시간 (분)

    # 비문 관련 설정
    NOSE_SIMILARITY_THRESHOLD: float = 0.75 # 비문 유사도 임계값 기본값 (조정 필요)

    # 정적 파일 설정 (필요시 추가)
    # STATIC_FILES_PATH: str = "app/static" # 정적 파일 경로

    #--------비문 모델 설정--------- 
    ML_MODEL_PATH: str
    BACKBONE_NAME: str = "seresnext50_ibn_custom"
    BACKBONE_IN_FEATURES: int = 2048
    FEATURE_DIM: int = 512
    MODEL_PRETRAINED: bool = False # backbone 사전학습 사용 여부
    DEVICE: str = "cpu"
    
    
    
    model_config = SettingsConfigDict(
        env_file=".env",          # .env 파일에서 설정을 로드하도록 지정
        env_file_encoding="utf-8" # .env 파일 인코딩
    )

# Settings 클래스의 인스턴스를 생성하여 애플리케이션 전체에서 임포트하여 사용합니다.
settings = Settings()

# 예시: 로드된 설정 값 확인
# print(f"Project Name: {settings.PROJECT_NAME}")
# print(f"Debug Mode: {settings.DEBUG}")
# print(f"Database URL: {settings.DATABASE_URL}") # SecretStr는 repr() 시 값이 *로 표시됨
# print(f"Secret Key: {settings.SECRET_KEY}")
# print(f"Nose Similarity Threshold: {settings.NOSE_SIMILARITY_THRESHOLD}")