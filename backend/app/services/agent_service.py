from typing import List, Dict
from datetime import datetime, timedelta
import pandas as pd
from app.core.data_loader import get_data_loader
from app.services.llm_agent import MatAgent
from sqlmodel import Session


class AgentService:
    def __init__(self, session: Session = None):
        self.session = session
        self.data = get_data_loader()
        self.llm_agent = MatAgent()

    # ------------------------------------------------------------------
    # Helper: product_id → description lookup
    # ------------------------------------------------------------------
    def _desc(self, product_id: str) -> str:
        row = self.data.product[self.data.product["product_id"] == str(product_id)]
        if not row.empty:
            return row.iloc[0]["description"]
        row = self.data.prod_plan_code_map[self.data.prod_plan_code_map["product_id"] == str(product_id)]
        if not row.empty:
            return row.iloc[0]["description"]
        return str(product_id)

    # ------------------------------------------------------------------
    # Public: generate AI response (ReAct LLM based)
    # ------------------------------------------------------------------
    def generate_ai_response(self, user_query: str) -> str:
        """
        기존의 룰 기반 방식을 대체하여 ReAct 에이전트를 호출합니다.
        """
        return self.llm_agent.chat(user_query)

    def generate_ai_response_stream(self, user_query: str):
        """
        스트리밍 응답을 위한 제너레이터 (LangGraph stream 사용)
        """
        from langchain_core.messages import HumanMessage
        config = {"configurable": {"thread_id": "api_stream"}}
        input_msg = HumanMessage(content=user_query)
        
        for event in self.llm_agent.graph.stream({"messages": [input_msg]}, config, stream_mode="values"):
            # 마지막 메시지의 내용만 스트리밍 (실제로는 더 복잡한 파싱이 필요할 수 있음)
            if "messages" in event:
                yield event["messages"][-1].content

    # ------------------------------------------------------------------
    # Public: alerts (Keeping original logic for dashboard)
    # ------------------------------------------------------------------
    def check_for_alerts(self) -> List[Dict[str, str]]:
        alerts = []
        today = pd.Timestamp("2026-03-26")

        # 1) 만기 60일 이내 배치
        bs = self.data.batch_stock.copy()
        bs["product_id"] = bs["product_id"].astype(str)
        threshold = today + timedelta(days=60)
        expiring = bs[bs["expiration_date"] <= threshold]
        for _, row in expiring.iterrows():
            desc = self._desc(str(row["product_id"]))
            remaining_days = (row["expiration_date"] - today).days
            alerts.append({
                "type": "expiry_warning",
                "message": f"만기 임박: {desc} (배치 {row['batch_no']}) — D-{remaining_days} ({row['expiration_date'].date()})",
                "item_name": desc,
                "timestamp": datetime.utcnow().isoformat(),
            })

        # 2) 미입고 발주 건
        po = self.data.purchase_order.copy()
        po["product_id"] = po["product_id"].astype(str)
        pending = po[po["schedule_qty"] > po["received_qty"]]
        for _, row in pending.iterrows():
            desc = self._desc(str(row["product_id"]))
            remaining = row["schedule_qty"] - row["received_qty"]
            alerts.append({
                "type": "pending_receipt",
                "message": f"미입고 발주: {desc} (PO {row['po_id']}) — {remaining}개 미입고",
                "item_name": desc,
                "timestamp": datetime.utcnow().isoformat(),
            })

        return alerts

    # ------------------------------------------------------------------
    # Audit log
    # ------------------------------------------------------------------
    def log_action(self, user_id: str, action: str, details: str, item_id: int = None):
        if self.session is None:
            return
        try:
            from app.models.inventory import AuditLog
            log = AuditLog(user_id=user_id, action=action, item_id=item_id, details=details)
            self.session.add(log)
            self.session.commit()
        except Exception:
            pass
