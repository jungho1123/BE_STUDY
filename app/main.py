# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# 설정 객체 임포트 (앱 이름, 디버그 모드 등을 설정 파일에서 가져올 수 있습니다.)
from app.core.config import settings

# 메인 API 라우터 임포트
# 이 라우터는 이미 다른 모든 하위 라우터들을 포함하고 있습니다.
from app.api.main_router import api_router

# FastAPI 애플리케이션 인스턴스 생성
# 설정 파일(settings)에서 앱 이름 등을 가져와 설정할 수 있습니다.
app = FastAPI(
    title=settings.PROJECT_NAME, # app/core/config.py에 PROJECT_NAME 설정이 있다고 가정
    # description="Your project description", # 필요에 따라 추가
    # version="1.0.0", # 필요에 따라 추가
    debug=settings.DEBUG # app/core/config.py에 DEBUG 설정이 있다고 가정
)

# --- 미들웨어 설정 (필요시 추가) ---
# CORS 미들웨어 예시 (프론트엔드와 연동 시 필요할 수 있습니다.)
# from fastapi.middleware.cors import CORSMiddleware
#
# origins = [
#     "http://localhost:3000",  # 프론트엔드 주소
#     "http://localhost:8000",  # 개발 서버 주소
#     # 배포 환경 주소 추가
# ]
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"], # 모든 HTTP 메서드 허용
#     allow_headers=["*"], # 모든 헤더 허용
# )
# 필요에 따라 다른 미들웨어 추가 (예: Authentication, Exception Handlers 등)


# --- 이벤트 핸들러 설정 (필요시 추가) ---
# 앱 시작/종료 시 실행될 함수 정의
# @app.on_event("startup")
# async def startup_event():
#     # 앱 시작 시 DB 연결, ML 모델 로드 등 작업 수행
#     print("Application startup event")
#     pass # 여기에 시작 로직 작성

# @app.on_event("shutdown")
# async def shutdown_event():
#     # 앱 종료 시 DB 연결 해제 등 작업 수행
#     print("Application shutdown event")
#     pass # 여기에 종료 로직 작성


# --- 라우터 포함 ---
# 메인 API 라우터를 FastAPI 애플리케이션에 연결합니다.
# 이렇게 하면 main_router에 포함된 모든 하위 엔드포인트에 접근 가능하게 됩니다.
app.include_router(api_router)


# --- 정적 파일 설정 ---
# dir.txt 구조에서 app/static/uploads 디렉토리가 있었습니다.
# /static 경로로 접근하면 app/static 디렉토리의 파일들을 제공하도록 설정합니다.
# 클라이언트는 "YOUR_APP_URL/static/uploads/your_image.jpg" 와 같이 접근할 수 있습니다.
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# --- 앱 실행 (uvicorn이 이 부분을 참조합니다) ---
# 이 파일 자체를 직접 실행할 때는 아래 주석을 해제하여 테스트할 수 있습니다.
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)