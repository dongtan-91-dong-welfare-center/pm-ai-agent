from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, create_engine

class RawMaterial(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item_name: str = Field(index=True)
    category: str
    current_stock: float
    safety_stock: float
    threshold: float
    unit: str
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class Supplier(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    lead_time: int  # in days
    risk_score: float  # 0.0 to 1.0

class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    action: str
    item_id: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: str
