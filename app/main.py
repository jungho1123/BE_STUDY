# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# 설정 객체 임포트
from app.core.config import settings

# 메인 API 라우터 임포트
from app.api.main_router import api_router

# 비문 벡터 처리 유틸리티에서 모델 로드 함수 임포트
# app/utils/vector_processor.py 파일에 정의된 load_ml_model 함수
from app.utils.vector_processor import load_ml_model


# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    # description="Your project description",
    # version="1.0.0",
    debug=settings.DEBUG
)

# --- 미들웨어 설정 (필요시 추가) ---
# CORS 미들웨어 예시
# from fastapi.middleware.cors import CORSMiddleware
# origins = ["*"] # 개발 시 모든 오리진 허용 (운영 시에는 특정 오리진만 허용)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# --- 이벤트 핸들러 설정 ---

@app.on_event("startup")
async def startup_event():
    """
    애플리케이션 시작 시 실행되는 이벤트 핸들러.
    머신러닝 모델 로드 등 초기화 작업을 수행합니다.
    """
    print("Application startup event triggered.")
    # 비문 특징 추출 모델 및 변환 객체 로드
    # app/utils/vector_processor.py 파일의 load_ml_model 함수 호출
    # load_ml_model 함수가 async 함수가 아니라면 await를 붙이지 않습니다.
    # 현재 vector_processor.py의 load_ml_model은 async가 아니므로 await를 제거합니다.
    load_ml_model() # 모델 로드 함수 호출
    print("ML model loading initiated.")

    # TODO: 안구 질환 예측 모델 로드 함수가 있다면 여기서 함께 호출

    # TODO: DB 연결 풀 초기화 등 다른 startup 작업 수행


@app.on_event("shutdown")
async def shutdown_event():
    """
    애플리케이션 종료 시 실행되는 이벤트 핸들러.
    DB 연결 해제 등 정리 작업을 수행합니다.
    """
    print("Application shutdown event triggered.")
    # TODO: DB 연결 풀 해제 등 정리 로직 작성
    pass


# --- 라우터 포함 ---
# 메인 API 라우터를 FastAPI 애플리케이션에 연결합니다.
app.include_router(api_router)


# --- 정적 파일 설정 ---
# /static 경로로 접근하면 app/static 디렉토리의 파일들을 제공하도록 설정합니다.
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# --- 앱 실행 (uvicorn이 이 부분을 참조합니다) ---
# 이 파일 자체를 직접 실행할 때는 아래 주석을 해제하여 테스트할 수 있습니다.
# if __name__ == "__main__":
#     import uvicorn
#     # --reload 옵션을 사용하면 코드 변경 시 자동 재시작됩니다.
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)