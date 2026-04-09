# 2026-04-08 [API_DESIGN.md#발주서-초안-생성] 발주서 API
# Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#2-엔드포인트-설계

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.core.db import get_db
from app.models.domain import Material, Vendor, VendorItem, PurchaseOrder, POStatus


router = APIRouter()


# 2026-04-08 [API_DESIGN.md] Pydantic 응답 스키마
# Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#응답-스키마-purchaseorderresponse
class PurchaseOrderResponse(BaseModel):
    """
    발주서 상세 정보

    데이터 출처: SAP EKKO (구매주문 헤더) + EKPO (구매주문 항목)
    포함 범위: MVP (po_item_no 제외 - 단일 품목만 지원)

    Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#응답-스키마-purchaseorderresponse
    """
    po_id: int = Field(..., description="발주서 번호")

    # 2026-04-08 [API_DESIGN.md] 발주 내용
    # Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#발주-내용-mvp-단일-품목
    product_id: int = Field(..., description="상품 ID")
    product_name: str = Field(..., description="상품명")
    vendor_id: int = Field(..., description="벤더 ID")
    vendor_name: str = Field(..., description="벤더명")

    # 2026-04-08 [API_DESIGN.md] 수량 및 가격
    # Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#수량-및-가격-mvp
    schedule_qty: float = Field(..., description="발주 수량")
    unit_price: float = Field(..., description="단위 가격")
    total_price: float = Field(..., description="총 금액")
    currency: str = Field(default="KRW", description="발주 통화")

    # 2026-04-08 [API_DESIGN.md] 일정 및 상태
    po_date: datetime = Field(..., description="발주 일자")
    status: str = Field(..., description="발주 상태 (DRAFT/APPROVED/SHIPPED/RECEIVED)")

    # 2026-04-08 [API_DESIGN.md] 추적 정보
    created_by_agent: bool = Field(..., description="AI Agent 자동 생성 여부")
    created_at: datetime = Field(..., description="DB 생성 시각")

    class Config:
        from_attributes = True


class CreatePORequest(BaseModel):
    """
    발주서 초안 생성 요청

    호출자: AI Agent만 호출 가능
    생성 상태: 항상 DRAFT (요청값 무시)

    Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#요청-스키마-createporequest
    """
    product_id: int = Field(..., description="구매할 상품 ID")
    vendor_id: int = Field(..., description="선택된 벤더 ID")
    schedule_qty: float = Field(..., gt=0, description="발주 수량 (양수)")

    # 2026-04-08 [API_DESIGN.md] 발주 사유 (AI Agent 설명)
    # Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#요청-스키마-createporequest
    reason: str = Field(
        ...,
        max_length=500,
        description="발주 사유 (AI Agent 설명)"
    )

    created_by_agent: bool = Field(default=True, description="AI Agent 플래그")


class CreatePOResponse(BaseModel):
    """
    발주서 초안 생성 응답

    Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#응답-스키마-createporesponse
    """
    po_id: int = Field(..., description="새로 생성된 발주서 번호")
    status: str = Field(default="DRAFT", description="생성 상태 (항상 DRAFT)")
    product_id: int
    vendor_id: int
    schedule_qty: float
    unit_price: float
    total_price: float = Field(..., description="총 금액 (자동 계산)")
    currency: str
    po_date: datetime
    message: str


class ApprovePORequest(BaseModel):
    """
    발주서 승인 요청

    호출자: 인간 PM만 호출 가능

    Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#요청-스키마-approvepo
    """
    approved_by: str = Field(..., description="승인자 식별 (이메일 또는 사원ID)")
    notes: str = Field(default="", max_length=500, description="승인 시 추가 메모")


class ApprovePOResponse(BaseModel):
    """
    발주서 승인 응답

    Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#응답-스키마-approveporesponse
    """
    po_id: int
    status: str
    approved_by: str
    approved_at: datetime
    message: str


# ============================================================================
# READ APIs (AI Agent 조회 자유)
# ============================================================================

@router.get("/purchase-orders", response_model=List[PurchaseOrderResponse])
def get_all_purchase_orders(
    status: Optional[str] = Query(None, description="필터: 발주 상태 (DRAFT, APPROVED 등)"),
    db: Session = Depends(get_db)
):
    """
    발주서 목록 조회 (필터 가능)

    2026-04-08 [API_DESIGN.md#c-기존-발주서-조회]
    Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#엔드포인트-2

    Parameters:
        status: 발주 상태 필터 (선택사항)

    Returns:
        List[PurchaseOrderResponse]: 발주서 목록
    """
    query = db.query(PurchaseOrder)

    # 2026-04-08 [API_DESIGN.md] 상태 필터 (선택사항)
    if status:
        query = query.filter(PurchaseOrder.status == status)

    purchase_orders = query.all()

    results = []
    for po in purchase_orders:
        material = db.query(Material).filter(Material.id == po.material_id).first()
        vendor = db.query(Vendor).filter(Vendor.id == po.vendor_id).first()

        results.append(PurchaseOrderResponse(
            po_id=po.id,
            product_id=po.material_id,
            product_name=material.name if material else "Unknown",
            vendor_id=po.vendor_id,
            vendor_name=vendor.name if vendor else "Unknown",
            schedule_qty=float(po.order_quantity),
            unit_price=float(po.total_price / po.order_quantity) if po.order_quantity > 0 else 0,
            total_price=float(po.total_price),
            currency="KRW",
            po_date=po.created_at,
            status=po.status.value,
            created_by_agent=True,  # 현재는 모두 agent 생성으로 처리
            created_at=po.created_at
        ))

    return results


@router.get("/purchase-orders/{po_id}", response_model=PurchaseOrderResponse)
def get_purchase_order(
    po_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 발주서 조회

    2026-04-08 [API_DESIGN.md#c-기존-발주서-조회]
    Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#엔드포인트-2

    Parameters:
        po_id: 발주서 번호

    Returns:
        PurchaseOrderResponse: 발주서 상세정보

    Raises:
        404: 발주서를 찾을 수 없음
    """
    purchase_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()

    if not purchase_order:
        raise HTTPException(
            status_code=404,
            detail=f"Purchase order not found (po_id={po_id})"
        )

    material = db.query(Material).filter(Material.id == purchase_order.material_id).first()
    vendor = db.query(Vendor).filter(Vendor.id == purchase_order.vendor_id).first()

    return PurchaseOrderResponse(
        po_id=purchase_order.id,
        product_id=purchase_order.material_id,
        product_name=material.name if material else "Unknown",
        vendor_id=purchase_order.vendor_id,
        vendor_name=vendor.name if vendor else "Unknown",
        schedule_qty=float(purchase_order.order_quantity),
        unit_price=float(purchase_order.total_price / purchase_order.order_quantity) if purchase_order.order_quantity > 0 else 0,
        total_price=float(purchase_order.total_price),
        currency="KRW",
        po_date=purchase_order.created_at,
        status=purchase_order.status.value,
        created_by_agent=True,
        created_at=purchase_order.created_at
    )


# ============================================================================
# WRITE APIs (AI Agent 제한: DRAFT만 생성, PM만 승인)
# ============================================================================

@router.post("/purchase-orders", response_model=CreatePOResponse)
def create_purchase_order(
    request: CreatePORequest,
    db: Session = Depends(get_db)
):
    """
    발주서 초안 생성 (AI Agent만 호출)

    2026-04-08 [API_DESIGN.md#발주서-초안-생성]
    Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#발주서-초안-생성

    보안:
    - status는 항상 'DRAFT'로 강제 설정
    - unit_price는 DB에서 벤더별 현재가로 조회
    - total_price는 자동 계산

    Parameters:
        request: CreatePORequest

    Returns:
        CreatePOResponse: 생성된 발주서 정보

    Raises:
        404: 상품 또는 벤더를 찾을 수 없음
        400: 벤더-상품 조합이 없음
    """
    # 2026-04-08 [API_DESIGN.md] 상품 존재 확인
    material = db.query(Material).filter(Material.id == request.product_id).first()
    if not material:
        raise HTTPException(
            status_code=404,
            detail=f"Product not found (product_id={request.product_id})"
        )

    # 2026-04-08 [API_DESIGN.md] 벤더 존재 확인
    vendor = db.query(Vendor).filter(Vendor.id == request.vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=404,
            detail=f"Vendor not found (vendor_id={request.vendor_id})"
        )

    # 2026-04-08 [API_DESIGN.md] 벤더-상품 단가 정보 조회
    vendor_item = db.query(VendorItem).filter(
        VendorItem.vendor_id == request.vendor_id,
        VendorItem.material_id == request.product_id
    ).first()

    if not vendor_item:
        raise HTTPException(
            status_code=400,
            detail=f"No vendor pricing found for product_id={request.product_id}, vendor_id={request.vendor_id}"
        )

    # 2026-04-08 [API_DESIGN.md] 발주서 생성 (status는 항상 DRAFT)
    # Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#보안-및-검증-규칙
    unit_price = vendor_item.unit_price
    total_price = request.schedule_qty * unit_price

    new_po = PurchaseOrder(
        po_number=f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}",  # 임시 PO 번호 (향후 SAP과 연동)
        vendor_id=request.vendor_id,
        material_id=request.product_id,
        order_quantity=int(request.schedule_qty),
        total_price=total_price,
        status=POStatus.DRAFT,  # 2026-04-08 [API_DESIGN.md] 항상 DRAFT
        reasoning_log=request.reason,
        created_at=datetime.utcnow()
    )

    db.add(new_po)
    db.commit()
    db.refresh(new_po)

    return CreatePOResponse(
        po_id=new_po.id,
        status="DRAFT",
        product_id=request.product_id,
        vendor_id=request.vendor_id,
        schedule_qty=request.schedule_qty,
        unit_price=unit_price,
        total_price=total_price,
        currency="KRW",
        po_date=new_po.created_at,
        message="Purchase order created as DRAFT. Awaiting PM approval."
    )


@router.patch("/purchase-orders/{po_id}/approve", response_model=ApprovePOResponse)
def approve_purchase_order(
    po_id: int,
    request: ApprovePORequest,
    db: Session = Depends(get_db)
):
    """
    발주서 승인 (PM만 호출)

    2026-04-08 [API_DESIGN.md#발주서-승인]
    Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#발주서-승인

    보안:
    - DRAFT 상태만 승인 가능
    - 다른 상태로의 변경은 불가

    Parameters:
        po_id: 발주서 번호
        request: ApprovePORequest

    Returns:
        ApprovePOResponse: 승인된 발주서 정보

    Raises:
        404: 발주서를 찾을 수 없음
        400: DRAFT 상태가 아님
    """
    # 2026-04-08 [API_DESIGN.md] 발주서 존재 확인
    purchase_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()

    if not purchase_order:
        raise HTTPException(
            status_code=404,
            detail=f"Purchase order not found (po_id={po_id})"
        )

    # 2026-04-08 [API_DESIGN.md] DRAFT 상태만 승인 가능
    # Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#보안-및-검증-규칙
    if purchase_order.status != POStatus.DRAFT:
        raise HTTPException(
            status_code=400,
            detail=f"Only DRAFT PO can be approved (current status: {purchase_order.status.value})"
        )

    # 2026-04-08 [API_DESIGN.md] 발주서 승인 처리
    purchase_order.status = POStatus.APPROVED
    purchase_order.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(purchase_order)

    return ApprovePOResponse(
        po_id=purchase_order.id,
        status=purchase_order.status.value,
        approved_by=request.approved_by,
        approved_at=purchase_order.approved_at,
        message="Purchase order approved. Ready for submission to vendor."
    )
