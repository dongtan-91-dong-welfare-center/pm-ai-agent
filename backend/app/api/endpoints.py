# from fastapi import APIRouter, Depends, HTTPException, Query
# from fastapi.responses import StreamingResponse, Response
# from sqlmodel import Session, select
# from app.core.db import get_db
# from app.models.inventory import RawMaterial, AuditLog
# from app.services.agent_service import AgentService
# from app.services.report_generator import generate_excel_report
# from typing import List
# import pandas as pd

# from app.core.data_loader import get_data_loader

# router = APIRouter()

# @router.get("/inventory")
# def get_inventory():
#     data = get_data_loader()
#     ws = data.warehouse_stock.copy()
#     prod = data.product[["product_id", "description", "base_unit"]].copy()
    
#     # Merge for better API response
#     ws["product_id"] = ws["product_id"].astype(str)
#     prod["product_id"] = prod["product_id"].astype(str)
#     merged = ws.merge(prod, on="product_id", how="left")
    
#     return merged.to_dict(orient="records")

# @router.post("/chat")
# def chat_with_agent(query: str, stream: bool = False, session: Session = Depends(get_session)):
#     agent = AgentService(session)
    
#     if stream:
#         return StreamingResponse(
#             agent.generate_ai_response_stream(query),
#             media_type="text/event-stream"
#         )
    
#     response = agent.generate_ai_response(query)
#     # Log the interaction
#     agent.log_action(user_id="user_01", action="CHAT", details=f"User: {query} | AI: {response}")
#     return {"response": response}

# @router.get("/report/excel")
# def download_excel_report(type: str = Query(..., description="Report type (e.g., 'nc', 'inventory')")):
#     data_loader = get_data_loader()
    
#     if type == "nc":
#         df = data_loader.non_conformance.copy()
#         title = "Non-Conformance Report"
#     elif type == "inventory":
#         df = data_loader.warehouse_stock.copy()
#         title = "Warehouse Stock Report"
#     else:
#         # Default to product list
#         df = data_loader.product.copy()
#         title = "Material Master Report"
        
#     excel_data = generate_excel_report(df, title)
    
#     return Response(
#         content=excel_data,
#         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         headers={"Content-Disposition": f"attachment; filename=MatAgent_{type}_Report.xlsx"}
#     )

# @router.get("/alerts")
# def get_alerts():
#     agent = AgentService()
#     return agent.check_for_alerts()
