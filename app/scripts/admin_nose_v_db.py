import pandas as pd
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.nose import NoseVector
from app import models  # 전체 모델 등록 (중요)
from app.core.time import get_kst_now

CSV_PATH = "C:/AI/SIXTHSENSE/dog_nose_cos/checkpoints/seresnext50_ibn_custom_nose_vectors_mean.csv"
USER_ID = 1  # 고정된 관리자 계정

def insert_vectors_fixed():
    df = pd.read_csv(CSV_PATH)
    db: Session = SessionLocal()

    for _, row in df.iterrows():
      
        vector_values = [row[f"f{i}"] for i in range(512)]

       
        vector = NoseVector(
            class_id=row["class_id"],
            user_id=USER_ID,
            vector=vector_values,
            created_at=get_kst_now()
        )

        db.add(vector)

    db.commit()
    db.close()
    print("[INFO] 모든 벡터 삽입 완료")

if __name__ == "__main__":
    insert_vectors_fixed()
