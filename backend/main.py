from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.core.db import init_db
from app.core.data_loader import get_data_loader
import uvicorn

app = FastAPI(title="On-premise AI Agent for Raw Material Management")


@app.on_event("startup")
def on_startup():
    # Initialize SQLite schema (for audit logs)
    init_db()
    # Pre-load all CSV data files
    get_data_loader()


app.include_router(api_router, prefix="/v1")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
