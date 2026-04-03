# backend/app/core/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Podman으로 띄운 PostgreSQL 접속 정보
DATABASE_URL = "postgresql://admin:admin@localhost:5432/pm_agent"

# 엔진 생성
engine = create_engine(DATABASE_URL, echo=True) # echo=True로 두면 SQL 로그가 터미널에 출력됩니다.

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 베이스 클래스
Base = declarative_base()

# FastAPI 의존성 주입용 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()