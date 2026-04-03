# backend/app/models/domain.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from pgvector.sqlalchemy import Vector

from backend.app.core.db import Base


# 발주서 상태 정의 (권한 티어 관리를 위한 Enum)
class POStatus(str, enum.Enum):
    DRAFT = "DRAFT"  # 에이전트가 생성한 가주문 (Tier 2)
    PENDING_APPROVAL = "PENDING"  # PM 승인 대기
    APPROVED = "APPROVED"  # PM 승인 완료 (Tier 3)
    REJECTED = "REJECTED"  # PM 반려
    COMPLETED = "COMPLETED"  # 입고 완료


class Material(Base):
    """원자재 마스터 테이블"""
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    material_code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # 나중에 RAG(검색 증강 생성)를 위해 원자재 설명을 벡터화하여 저장할 컬럼
    description_embedding = Column(Vector(1536), nullable=True)

    safety_stock = Column(Integer, nullable=False, default=0)  # 안전 재고 (트리거 기준점)
    unit = Column(String, nullable=False, default="EA")  # 단위

    # 관계 설정
    stock = relationship("WarehouseStock", back_populates="material", uselist=False)
    vendor_items = relationship("VendorItem", back_populates="material")


class WarehouseStock(Base):
    """창고 재고 테이블"""
    __tablename__ = "warehouse_stocks"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), unique=True, nullable=False)
    current_quantity = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    material = relationship("Material", back_populates="stock")


class Vendor(Base):
    """공급업체(벤더) 테이블"""
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    vendor_code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    reliability_score = Column(Float, default=5.0)  # 벤더 신뢰도 (에이전트 판단 지표)

    items = relationship("VendorItem", back_populates="vendor")
    purchase_orders = relationship("PurchaseOrder", back_populates="vendor")


class VendorItem(Base):
    """벤더별 원자재 단가 및 리드타임 정보 (에이전트가 벤더를 비교하는 핵심 데이터)"""
    __tablename__ = "vendor_items"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)

    unit_price = Column(Float, nullable=False)  # 단가
    lead_time_days = Column(Integer, nullable=False)  # 납기 소요 시간(일)
    min_order_qty = Column(Integer, default=1)  # 최소 주문 수량

    vendor = relationship("Vendor", back_populates="items")
    material = relationship("Material", back_populates="vendor_items")


class PurchaseOrder(Base):
    """발주서 테이블"""
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String, unique=True, index=True, nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)

    order_quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)

    # 핵심: 에이전트는 무조건 DRAFT로만 생성하도록 로직에서 강제해야 함
    status = Column(Enum(POStatus), default=POStatus.DRAFT, nullable=False)

    reasoning_log = Column(Text, nullable=True)  # 에이전트가 이 벤더를 선택한 이유를 기록 (비대칭 로깅용)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)

    vendor = relationship("Vendor", back_populates="purchase_orders")
    material = relationship("Material")