# backend/migrate_csv.py
import pandas as pd
from sqlalchemy.orm import Session
from backend.app.core.db import SessionLocal
from backend.app.models.domain import Material, WarehouseStock, Vendor, VendorItem, PurchaseOrder, POStatus


def run_migration():
    db: Session = SessionLocal()
    print("CSV 데이터 마이그레이션을 시작합니다...")

    try:
        # --- 1. Vendor (벤더) 마이그레이션 ---
        print("1. Vendor 데이터 적재 중...")
        vendor_df = pd.read_csv("backend/data/vendor.csv")
        vendor_df = vendor_df.drop_duplicates(subset=['vendor_id'])

        for _, row in vendor_df.iterrows():
            vendor_code = str(row['vendor_id'])
            # 중복 확인
            existing_vendor = db.query(Vendor).filter(Vendor.vendor_code == vendor_code).first()
            if not existing_vendor:
                new_vendor = Vendor(
                    vendor_code=vendor_code,
                    name=row['vendor_name'],
                    reliability_score=5.0  # 기본값
                )
                db.add(new_vendor)
        db.commit()

        # --- 2. Material (원자재) 마이그레이션 ---
        print("2. Material 데이터 적재 중...")
        # 여러 CSV에서 고유 product_id 추출
        stock_df = pd.read_csv("backend/data/warehouse_stock.csv")
        po_df = pd.read_csv("backend/data/purchase_order.csv")

        unique_product_ids = set(stock_df['product_id'].unique()) | set(po_df['product_id'].unique())

        for p_id in unique_product_ids:
            material_code = str(p_id)
            existing_material = db.query(Material).filter(Material.material_code == material_code).first()
            if not existing_material:
                new_material = Material(
                    material_code=material_code,
                    name=f"원자재_{material_code}",  # 임시 이름 (product.csv가 없으므로)
                    safety_stock=100,  # 임시 안전재고 (테스트용)
                    unit="EA"
                )
                db.add(new_material)
        db.commit()

        # --- 3. WarehouseStock (창고 재고) 마이그레이션 ---
        print("3. WarehouseStock 데이터 적재 중...")
        for _, row in stock_df.iterrows():
            material_code = str(row['product_id'])
            material = db.query(Material).filter(Material.material_code == material_code).first()

            if material:
                existing_stock = db.query(WarehouseStock).filter(WarehouseStock.material_id == material.id).first()
                if not existing_stock:
                    new_stock = WarehouseStock(
                        material_id=material.id,
                        current_quantity=int(row['unrestricted_qty'])
                    )
                    db.add(new_stock)
        db.commit()

        # --- 4. VendorItem (벤더별 단가 및 리드타임) 마이그레이션 ---
        print("4. VendorItem 데이터 적재 중...")
        vendor_item_df = pd.read_csv("backend/data/vendor_into_record.csv")

        for _, row in vendor_item_df.iterrows():
            vendor_code = str(row['vendor_id'])
            material_code = str(row['product_id'])

            vendor = db.query(Vendor).filter(Vendor.vendor_code == vendor_code).first()
            material = db.query(Material).filter(Material.material_code == material_code).first()

            if vendor and material:
                existing_item = db.query(VendorItem).filter(
                    VendorItem.vendor_id == vendor.id,
                    VendorItem.material_id == material.id
                ).first()

                if not existing_item:
                    new_item = VendorItem(
                        vendor_id=vendor.id,
                        material_id=material.id,
                        unit_price=float(row['unit_price']),
                        lead_time_days=7,  # CSV에 명시적 리드타임이 없어 7일로 가정
                        min_order_qty=1
                    )
                    db.add(new_item)
        db.commit()

        # --- 5. PurchaseOrder (발주서) 마이그레이션 ---
        print("5. PurchaseOrder 데이터 적재 중...")
        for _, row in po_df.iterrows():
            po_number = f"{row['po_id']}_{row['po_item_no']}"
            vendor_code = str(row['vendor_id'])
            material_code = str(row['product_id'])

            vendor = db.query(Vendor).filter(Vendor.vendor_code == vendor_code).first()
            material = db.query(Material).filter(Material.material_code == material_code).first()

            if vendor and material:
                existing_po = db.query(PurchaseOrder).filter(PurchaseOrder.po_number == po_number).first()
                if not existing_po:
                    # 기존 CSV 내역은 이미 처리된 것으로 간주하여 COMPLETED 상태 처리
                    status = POStatus.COMPLETED if row['received_qty'] > 0 else POStatus.PENDING_APPROVAL

                    new_po = PurchaseOrder(
                        po_number=po_number,
                        vendor_id=vendor.id,
                        material_id=material.id,
                        order_quantity=int(row['schedule_qty']),
                        total_price=0.0,  # 단가 연동 로직은 단순화를 위해 0 처리
                        status=status
                    )
                    db.add(new_po)
        db.commit()

        print("모든 마이그레이션이 성공적으로 완료되었습니다!")

    except Exception as e:
        db.rollback()
        print(f"마이그레이션 중 오류가 발생했습니다: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()