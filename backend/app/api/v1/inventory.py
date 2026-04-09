# 2026-04-08 [API_DESIGN.md#21-read-api-조회] 재고 조회 API
# Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#a-재고-조회

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.models.domain import Material, WarehouseStock
from pydantic import BaseModel, Field


router = APIRouter()


# 2026-04-08 [API_DESIGN.md] Pydantic 응답 스키마
# Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#응답-스키마-warehousestockresponse
class WarehouseStockResponse(BaseModel):
    """
    재고 조회 응답 스키마

    데이터 출처: SAP MARD (Material Master - Storage Location Data)
    포함 범위: MVP (배치 정보 제외)

    Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#응답-스키마-warehousestockresponse
    """
    product_id: int = Field(..., description="상품 ID (Material.id)")
    product_name: str = Field(..., description="상품명 (Material.name)")

    # 2026-04-08 [API_DESIGN.md] unrestricted_qty 매핑
    # SAP Column: MARD.LABST (제약 없이 사용 가능한 재고)
    # Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#-핵심-사용-가능-재고-mvp
    unrestricted_qty: float = Field(..., description="사용 가능 재고 (unrestricted_qty)")

    safety_stock_qty: float = Field(..., description="안전 재고 (PM 정의)")
    status: str = Field(..., description="상태: CRITICAL, LOW, SAFE")

    class Config:
        from_attributes = True


@router.get("/warehouse-stock/{product_id}", response_model=WarehouseStockResponse)
def get_warehouse_stock(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 상품의 재고 조회

    2026-04-08 [API_DESIGN.md#a-재고-조회]
    Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#엔드포인트

    Parameters:
        product_id: 상품 ID (Material.id)

    Returns:
        WarehouseStockResponse: 재고 정보

    Raises:
        404: 상품을 찾을 수 없음
    """
    # 2026-04-08 [API_DESIGN.md] 상품 정보 조회
    material = db.query(Material).filter(Material.id == product_id).first()
    if not material:
        raise HTTPException(
            status_code=404,
            detail=f"Product not found (product_id={product_id})"
        )

    # 2026-04-08 [API_DESIGN.md] 재고 정보 조회
    warehouse_stock = db.query(WarehouseStock).filter(
        WarehouseStock.material_id == product_id
    ).first()

    # 재고가 없으면 0으로 처리
    unrestricted_qty = warehouse_stock.current_quantity if warehouse_stock else 0

    # 2026-04-08 [API_DESIGN.md] 상태 판정 로직
    # CRITICAL: unrestricted_qty < safety_stock * 0.5
    # LOW: safety_stock * 0.5 <= unrestricted_qty < safety_stock
    # SAFE: unrestricted_qty >= safety_stock
    # Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#-상태-판정-계산
    safety_stock = material.safety_stock

    if unrestricted_qty < safety_stock * 0.5:
        status = "CRITICAL"
    elif unrestricted_qty < safety_stock:
        status = "LOW"
    else:
        status = "SAFE"

    return WarehouseStockResponse(
        product_id=material.id,
        product_name=material.name,
        unrestricted_qty=float(unrestricted_qty),
        safety_stock_qty=float(safety_stock),
        status=status
    )


@router.get("/warehouse-stock", response_model=List[WarehouseStockResponse])
def get_all_warehouse_stocks(db: Session = Depends(get_db)):
    """
    모든 상품의 재고 조회 (대시보드용)

    2026-04-08 [API_DESIGN.md#a-재고-조회]
    Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#엔드포인트

    Returns:
        List[WarehouseStockResponse]: 전체 재고 목록
    """
    materials = db.query(Material).all()

    results = []
    for material in materials:
        warehouse_stock = db.query(WarehouseStock).filter(
            WarehouseStock.material_id == material.id
        ).first()

        unrestricted_qty = warehouse_stock.current_quantity if warehouse_stock else 0
        safety_stock = material.safety_stock

        if unrestricted_qty < safety_stock * 0.5:
            status = "CRITICAL"
        elif unrestricted_qty < safety_stock:
            status = "LOW"
        else:
            status = "SAFE"

        results.append(WarehouseStockResponse(
            product_id=material.id,
            product_name=material.name,
            unrestricted_qty=float(unrestricted_qty),
            safety_stock_qty=float(safety_stock),
            status=status
        ))

    return results
