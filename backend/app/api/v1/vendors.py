# 2026-04-08 [API_DESIGN.md#b-벤더-및-단가-조회] 벤더 조회 API
# Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#b-벤더-및-단가-조회

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from pydantic import BaseModel, Field
from datetime import date

from app.core.db import get_db
from app.models.domain import Material, Vendor, VendorItem


router = APIRouter()


# 2026-04-08 [API_DESIGN.md] Pydantic 응답 스키마
# Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#응답-스키마-vendoritemresponse
class VendorItemResponse(BaseModel):
    """
    벤더별 구매 조건 (단가/리드타임/최소주문)

    데이터 출처: SAP vendor_info_record (구매정보기록)
    포함 범위: MVP (제조사/구매그룹 제외, Month 4 추가)

    Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#응답-스키마-vendoritemresponse
    """
    vendor_id: int = Field(..., description="벤더 ID")
    vendor_name: str = Field(..., description="벤더명")

    # 2026-04-08 [API_DESIGN.md] 구매 조건 (MVP 핵심)
    # SAP Column: INFOB.NETPR (단위 가격)
    # Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#-구매-조건-mvp-핵심
    unit_price: float = Field(..., description="단위 가격 (기본 통화)")

    # 2026-04-08 [API_DESIGN.md] 통화 코드
    # SAP Column: INFOB.WAERS
    # Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#-구매-조건-mvp-핵심
    currency: str = Field(default="KRW", description="통화 코드 (KRW, USD 등)")

    # 2026-04-08 [API_DESIGN.md] 발주 단위
    # SAP Column: INFOB.BSTME
    # Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#-추가-조건-mvp-향후-확장
    order_unit: str = Field(default="EA", description="발주 단위 (EA, BOX, KG 등)")

    # 2026-04-08 [API_DESIGN.md] 유효 기간 (Month 2 활용)
    # SAP Column: INFOB.DATAB / DATBE
    # Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#-추가-조건-mvp-향후-확장
    valid_from: Optional[date] = Field(None, description="유효 시작일 (Month 2 활용)")
    valid_to: Optional[date] = Field(None, description="유효 종료일 (Month 2 활용)")

    # 2026-04-08 [API_DESIGN.md] 고정 벤더 여부 (Month 3 활용)
    is_fixed_vendor: bool = Field(
        default=False,
        description="고정 벤더 여부 (Month 3 발주 제약 조건)"
    )

    class Config:
        from_attributes = True


class VendorItemListResponse(BaseModel):
    """
    특정 상품의 벤더 옵션 목록

    Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#응답-스키마-vendoritemlistresponse
    """
    product_id: int = Field(..., description="상품 ID")
    product_name: str = Field(..., description="상품명")
    vendor_options: List[VendorItemResponse] = Field(..., description="벤더 옵션 목록")

    class Config:
        from_attributes = True


@router.get("/vendor-items/{product_id}", response_model=VendorItemListResponse)
def get_vendor_items_for_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 상품의 모든 벤더 옵션 조회

    2026-04-08 [API_DESIGN.md#b-벤더-및-단가-조회]
    Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#엔드포인트-1

    AI Agent가 최적 벤더를 선택하기 위해 호출하는 핵심 API
    단가(unit_price) + 리드타임(lead_time_days) 비교용

    Parameters:
        product_id: 상품 ID

    Returns:
        VendorItemListResponse: 벤더 옵션 목록

    Raises:
        404: 상품을 찾을 수 없음
        400: 벤더 옵션이 없음
    """
    # 2026-04-08 [API_DESIGN.md] 상품 존재 확인
    material = db.query(Material).filter(Material.id == product_id).first()
    if not material:
        raise HTTPException(
            status_code=404,
            detail=f"Product not found (product_id={product_id})"
        )

    # 2026-04-08 [API_DESIGN.md] 벤더 옵션 조회
    vendor_items = db.query(VendorItem).filter(
        VendorItem.material_id == product_id
    ).all()

    if not vendor_items:
        raise HTTPException(
            status_code=400,
            detail=f"No vendor pricing found for product_id={product_id}"
        )

    # 2026-04-08 [API_DESIGN.md] 응답 구성
    vendor_options = []
    for item in vendor_items:
        vendor = db.query(Vendor).filter(Vendor.id == item.vendor_id).first()
        if vendor:
            vendor_options.append(VendorItemResponse(
                vendor_id=vendor.id,
                vendor_name=vendor.name,
                unit_price=item.unit_price,
                currency="KRW",  # SAP에서 export된 데이터의 기본 통화
                order_unit="EA",  # Month 2에 추가 예정
                valid_from=None,  # Month 2에 추가 예정
                valid_to=None,    # Month 2에 추가 예정
                is_fixed_vendor=False  # Month 3에 추가 예정
            ))

    return VendorItemListResponse(
        product_id=material.id,
        product_name=material.name,
        vendor_options=vendor_options
    )


@router.get("/vendors", response_model=List[VendorItemResponse])
def get_all_vendors(db: Session = Depends(get_db)):
    """
    모든 벤더 목록 조회 (참고용)

    2026-04-08 [API_DESIGN.md#b-벤더-및-단가-조회]
    Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#엔드포인트-1

    Returns:
        List[VendorItemResponse]: 전체 벤더 목록
    """
    vendors = db.query(Vendor).all()

    # 간단한 구현 - 나중에 필요시 확장
    return [
        VendorItemResponse(
            vendor_id=v.id,
            vendor_name=v.name,
            unit_price=0.0,  # 벤더 전체 조회이므로 단가는 없음
            currency="KRW",
            order_unit="EA",
            is_fixed_vendor=False
        )
        for v in vendors
    ]
