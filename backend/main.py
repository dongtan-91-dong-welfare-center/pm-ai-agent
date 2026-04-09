# 2026-04-08 [API_DESIGN.md] FastAPI 앱 초기화 (메인 엔트리포인트)
# Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#4-라우터-파일-구조

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 기존 라우터 (CSV 기반 - 임시 유지)
# from app.api.endpoints import router as api_router_v1_legacy

# 새로운 라우터 (PostgreSQL 기반 - MVP)
from app.api.v1 import inventory, vendors, purchase_orders, health

# 데이터베이스 초기화
from app.core.db import engine, Base
from app.core.data_loader import get_data_loader

# 2026-04-08 [API_DESIGN.md] PostgreSQL 테이블 자동 생성
# Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#2-엔드포인트-설계
Base.metadata.create_all(bind=engine)

# 2026-04-08 [API_DESIGN.md] FastAPI 앱 초기화
# Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#4-라우터-파일-구조
app = FastAPI(
    title="PM AI Agent API",
    description="원자재 관리 & 자동 발주 (LangGraph 기반 AI Agent)",
    version="0.1.0 (Month 1 MVP)",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 2026-04-08 CORS 설정 (향후 프론트엔드/외부 클라이언트 접근 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계에서는 모든 원본 허용 (production에서는 수정 필요)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """
    2026-04-08 애플리케이션 시작 이벤트
    - init_db(): SQLite 스키마 초기화 (기존)
    - get_data_loader(): CSV 데이터 프리로드 (기존)
    """
    from app.core.db import get_db
    get_db()
    get_data_loader()


# 2026-04-08 [API_DESIGN.md] 기존 v1 라우터 등록 (임시 유지)
# Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#새-구조안
# 기존: /v1/chat, /v1/report/excel, /v1/alerts (Month 2-3에 재구현 예정)
# app.include_router(api_router_v1_legacy, prefix="/v1")

# 2026-04-08 [API_DESIGN.md] 새로운 PostgreSQL 기반 라우터 등록 (MVP)
# Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#새-구조안
# 헬스 체크
app.include_router(health.router, tags=["Health"])

# 재고 조회 API
app.include_router(
    inventory.router,
    prefix="/api/v1",
    tags=["Inventory (READ)"]
)

# 벤더 조회 API
app.include_router(
    vendors.router,
    prefix="/api/v1",
    tags=["Vendors (READ)"]
)

# 발주서 API
app.include_router(
    purchase_orders.router,
    prefix="/api/v1",
    tags=["Purchase Orders (READ/WRITE)"]
)


if __name__ == "__main__":
    # 2026-04-08 개발 서버 실행
    # 실행: python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
    # 또는: python backend/main.py
    uvicorn.run(app, host="0.0.0.0", port=8000)
