# app/utils/vector_processor.py
import numpy as np
from typing import Optional, List
import io
from PIL import Image # 이미지 처리를 위해 Pillow 사용

# PyTorch 및 관련 라이브러리 임포트
import torch
import torch.nn.functional as F # 코사인 유사도 계산에 사용 (NumPy 대신 PyTorch 사용 시)
from torchvision import transforms # 이미지 변환 파이프라인 구성에 사용

# 우리가 정의한 모델 및 변환 관련 파일 임포트
# **주의: 이 임포트 경로는 파일 정리 단계에서 제안된 구조에 맞춰 작성되었습니다.**
# **실제 파일 위치에 따라 임포트 경로를 수정해야 합니다.**
from app.ml_models.nose_non_print.siamese_cosine import SiameseNetwork # app/ml_models/nose_non_print/ 디렉토리의 siamese_cosine.py
from app.ml_models.nose_non_print.transforms import get_val_transform # app/ml_models/nose_non_print/ 디렉토리의 transforms.py

# 설정 객체 임포트
from app.core.config import settings # app/core/config에 settings 객체가 정의되어 있다고 가정

# --- 모델 로드 및 변환 객체 (애플리케이션 구동 시 한 번만 로드) ---
# 이 변수들에 로드된 모델과 변환 객체가 저장됩니다.
_siamese_model: Optional[torch.nn.Module] = None
_val_transform: Optional[transforms.Compose] = None
_device: torch.device # 설정에서 장치 정보 가져옴 (load_ml_model에서 초기화)

def load_ml_model():
    """
    사전에 학습된 비문 특징 추출 모델과 검증용 이미지 변환 객체를 로드하는 함수.
    애플리케이션 시작 시 (main.py의 startup 이벤트) 호출되어야 합니다.
    """
    global _siamese_model, _val_transform, _device

    # 사용할 장치 설정 (config.py에서 가져옴)
    _device = torch.device(settings.DEVICE)

    if _siamese_model is None or _val_transform is None:
        print(f"Loading ML model from {settings.ML_MODEL_PATH} on device {_device}...")

        try:
            # 1. SiameseNetwork 모델 인스턴스 생성
            # config.py의 설정 값을 사용하여 모델 파라미터 지정
            # **SiameseNetwork 및 get_backbone 함수가 임포트 가능하거나 정의되어 있어야 합니다.**
            model = SiameseNetwork(
                 backbone_name=settings.BACKBONE_NAME,
                 in_features=settings.BACKBONE_IN_FEATURES, # Backbone 출력 차원 (예: 2048)
                 feature_dim=settings.FEATURE_DIM,         # Projector 출력 차원 (우리가 원하는 512)
                 pretrained=settings.MODEL_PRETRAINED      # Backbone 사전학습 사용 여부
             )

            # 2. 학습된 모델 가중치 로드
            # 모델 가중치 파일 경로: settings.ML_MODEL_PATH
            # CPU 또는 GPU 장치로 로드 (map_location 사용)
            state_dict = torch.load(settings.ML_MODEL_PATH, map_location=_device)
            model.load_state_dict(state_dict)

            # 3. 모델을 지정된 장치로 이동시키고 추론 모드로 설정
            model.to(_device)
            model.eval() # 추론 모드 설정 (Dropout, BatchNorm 등이 추론에 맞게 동작)

            _siamese_model = model
            print("ML model loaded successfully.")

            # 4. 검증용 이미지 변환 객체 생성
            # **get_val_transform 함수가 임포트 가능하거나 정의되어 있어야 합니다.**
            # transforms.py 파일을 참고하여 필요한 이미지 크기 지정 (학습 때 사용한 크기)
            _val_transform = get_val_transform(img_size=224) # transforms.py의 기본값 224 사용 또는 설정에서 가져옴
            print("Validation transform created.")

        except Exception as e:
            print(f"Error loading ML model or transform: {e}")
            _siamese_model = None # 로드 실패 시 None으로 유지
            _val_transform = None
            # 앱 시작 시 로드 실패는 치명적이므로 예외를 다시 발생시키는 것을 고려할 수 있습니다.
            # raise e


# --- 벡터 추출 함수 (ML 모델 연동) ---
# 이 함수는 app/api/nose/service.py에서 호출됩니다.
async def extract_nose_vector(image_bytes: bytes) -> Optional[List[float]]:
    """
    비문 이미지 파일 내용에서 특징 벡터를 추출하는 비동기 함수.
    로드된 ML 모델과 변환 객체를 사용합니다.
    성공 시 설정된 차원(settings.FEATURE_DIM, 예: 512)의 float 리스트를 반환하고,
    실패 시 None을 반환합니다.
    """
    # 모델과 변환 객체가 로드되었는지 확인 (load_ml_model 함수가 성공적으로 실행되었다고 가정)
    if _siamese_model is None or _val_transform is None:
        print("ML model or transform not loaded. Cannot extract vector.")
        # 모델 로드가 startup 이벤트에서 이루어지지 않았다면 여기서 load_ml_model() 호출을 시도할 수 있으나,
        # startup에서 처리하는 것이 로딩 지연을 피하는 좋은 방법입니다.
        # load_ml_model() # 필요시 여기서 로드 시도
        # if _siamese_model is None or _val_transform is None:
        #      print("ML model or transform failed to load on demand.")
        return None # 로드 실패 상태이면 벡터 추출 불가능

    try:
        # 1. 이미지 바이트를 PIL Image 객체로 변환
        # BytesIO를 사용하여 메모리 상의 바이트를 파일처럼 다룹니다.
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB") # RGB 채널로 변환 보장

        # 2. 검증용 이미지 변환 적용 (PyTorch Tensor로 변환 포함)
        # _val_transform은 torchvision.transforms.Compose 객체입니다.
        image_tensor = _val_transform(image) # 결과: [C, H, W] 형태의 Tensor

        # 3. 모델 입력 형식에 맞게 배치 차원 추가: [C, H, W] -> [B, C, H, W] (B=1)
        image_tensor = image_tensor.unsqueeze(0)

        # 4. 이미지를 모델과 동일한 장치로 이동
        image_tensor = image_tensor.to(_device)

        # 5. 모델 추론 (Inference) 수행 - SiameseNetwork의 extract 메서드 사용
        # extract 메서드는 정규화된 벡터를 반환합니다 (siamese_cosine.py 참고).
        with torch.no_grad(): # 추론 시에는 gradient 계산 비활성화하여 메모리 및 성능 최적화
             feature_tensor = _siamese_model.extract(image_tensor, normalize=True) # 결과: [B, FEATURE_DIM] 형태의 Tensor

        # 6. 결과 벡터 후처리 및 Python 리스트로 변환
        # 배치 차원 제거: [1, FEATURE_DIM] -> [FEATURE_DIM]
        # Tensor를 CPU로 이동 (.cpu()) 하고 NumPy 배열로 변환 (.numpy())
        # NumPy 배열을 Python 리스트로 변환 (.tolist())
        feature_vector_list = feature_tensor.squeeze(0).cpu().numpy().tolist()

        # 추출된 벡터 차원 확인 (settings.FEATURE_DIM과 일치하는지 확인)
        if len(feature_vector_list) != settings.FEATURE_DIM:
             print(f"Warning: Extracted vector dimension mismatch. Expected {settings.FEATURE_DIM}, got {len(feature_vector_list)}")
             # 차원이 다르면 오류로 처리할지, 그냥 반환할지 결정 필요. 여기서는 None 반환 예시.
             return None


        print(f"Vector extracted successfully. Dimension: {len(feature_vector_list)}")
        return feature_vector_list


    except Exception as e:
        print(f"Error during vector extraction: {e}")
        return None # 오류 발생 시 None 반환

# --- 코사인 유사도 계산 함수 ---
# 이 함수는 app/api/nose/service.py에서 호출됩니다.
# NumPy를 사용하는 기존 구현 유지
def calculate_cosine_similarity(vector1: List[float], vector2: List[float]) -> float:
    """
    두 벡터 간의 코사인 유사도를 계산하는 함수.
    NumPy를 사용하여 효율적으로 계산합니다.
    """
    if not vector1 or not vector2:
        print("Warning: Cannot calculate similarity with empty vectors.")
        return 0.0

    # 두 벡터의 차원이 다르면 유사도 계산 불가
    if len(vector1) != len(vector2):
        print(f"Error: Vector dimension mismatch for similarity calculation: {len(vector1)} vs {len(vector2)}")
        return 0.0

    try:
        # Python 리스트를 NumPy 배열로 변환
        np_vector1 = np.array(vector1, dtype=np.float32)
        np_vector2 = np.array(vector2, dtype=np.float32)

        # 두 벡터의 내적 계산
        dot_product = np.dot(np_vector1, np_vector2)

        # 각 벡터의 L2 노름(크기) 계산
        norm_vector1 = np.linalg.norm(np_vector1)
        norm_vector2 = np.linalg.norm(np_vector2)

        # 노름이 0이면 유사도를 계산할 수 없으므로 0 반환
        if norm_vector1 == 0 or norm_vector2 == 0:
            return 0.0

        # 코사인 유사도 계산
        similarity = dot_product / (norm_vector1 * norm_vector2)

        # 결과가 부동소수점 오차로 인해 -1.0 ~ 1.0 범위를 살짝 벗어날 수 있으므로 클리핑
        return float(np.clip(similarity, -1.0, 1.0))

    except Exception as e:
        print(f"Error calculating cosine similarity: {e}")
        return 0.0 # 오류 발생 시 0.0 반환 (또는 예외 발생)