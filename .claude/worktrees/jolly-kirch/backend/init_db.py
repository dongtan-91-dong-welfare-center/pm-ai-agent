# backend/init_db.py
from backend.app.core.db import engine, Base
# 생성할 모델들을 반드시 import 해야 Base.metadata.create_all이 인식합니다.
from backend.app.models.domain import Material, WarehouseStock, Vendor, VendorItem, PurchaseOrder

def init_database():
    print("PostgreSQL에 테이블 생성을 시작합니다...")
    # 등록된 모든 모델의 스키마를 DB에 생성 (이미 존재하면 무시됨)
    Base.metadata.create_all(bind=engine)
    print("테이블 생성 완료!")

if __name__ == "__main__":
    init_database()