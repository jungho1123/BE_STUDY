# app/api/main_router.py
from fastapi import APIRouter

# 개별 도메인의 라우터 모듈 임포트

# Auth 라우터 임포트 (app/api/auth/router.py 에 정의되어 있다고 가정)
# 만약 user.py, nose.py와 함께 올려주신 router.py가 Auth 라우터라면,
# 해당 파일을 app/api/auth/router.py 로 옮기고 임포트 경로를 맞춰야 합니다.
from app.api.auth.router import router as auth_router

# Nose 라우터 임포트 (우리가 방금 작업한 app/api/nose/router.py 에 정의)
from app.api.nose.router import router as nose_router

# 다른 도메인의 라우터 임포트 (dir.txt 구조 기반, 실제 파일 존재 시)
# from app.api.comic.router import router as comic_router
# from app.api.dog_posts.router import router as dog_posts_router
# from app.api.eye.router import router as eye_router


# 메인 API 라우터 인스턴스 생성
# 이 라우터 자체에는 prefix를 설정하지 않아도 됩니다.
# 각 하위 라우터에 설정된 prefix가 적용됩니다. (예: /auth, /nose)
api_router = APIRouter()

# 개별 라우터들을 메인 라우터에 포함
# include_router() 메서드를 사용하여 다른 라우터 인스턴스를 추가합니다.

# Auth 라우터 포함 (prefix가 /auth로 설정되어 있을 것임)
api_router.include_router(auth_router)

# Nose 라우터 포함 (prefix가 /nose로 설정되어 있을 것임)
api_router.include_router(nose_router)

# 다른 도메인 라우터 포함 (주석 해제 및 임포트 경로 확인 필요)
# api_router.include_router(comic_router)
# api_router.include_router(dog_posts_router)
# api_router.include_router(eye_router)

# 이 api_router 인스턴스는 app/main.py에서 FastAPI 앱에 연결됩니다.