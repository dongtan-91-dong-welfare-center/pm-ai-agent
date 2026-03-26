from typing import Annotated, List, TypedDict, Union, Dict
import os
import pandas as pd
from datetime import datetime, timedelta
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from app.core.data_loader import get_data_loader

# --- State Definition ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    # You can add more state variables here if needed (e.g., intermediate_steps)

# --- Helper Function ---
def _get_desc(product_id: str) -> str:
    """product_id를 기반으로 품목명을 조회합니다."""
    data = get_data_loader()
    product_id = str(product_id)
    # product.csv에서 검색
    row = data.product[data.product["product_id"] == product_id]
    if not row.empty:
        return row.iloc[0]["description"]
    # prod_plan_code_map.csv에서 검색
    row = data.prod_plan_code_map[data.prod_plan_code_map["product_id"] == product_id]
    if not row.empty:
        return row.iloc[0]["description"]
    return product_id

# --- Tool Definitions ---

@tool
def query_inventory(product_id: str = None):
    """
    창고 재고(Warehouse Stock) 및 배치 재고(Batch Stock) 정보를 상세히 조회합니다.
    product_id가 주어지면 해당 자재의 가용량, 검사 중 수량, 블로킹 수량 및 배치를 확인합니다.
    """
    data = get_data_loader()
    product_id = str(product_id) if product_id else None
    
    ws = data.warehouse_stock.copy()
    bs = data.batch_stock.copy()
    
    if product_id:
        ws = ws[ws["product_id"] == product_id]
        bs = bs[bs["product_id"] == product_id]
    
    if ws.empty and bs.empty:
        return f"품목 {product_id}에 대한 재고 정보가 없습니다."

    name = _get_desc(product_id) if product_id else "전체"
    result = f"### [재고 현황: {name}({product_id if product_id else 'All'})]\n"
    for _, row in ws.iterrows():
        id_ = str(row['product_id'])
        desc = _get_desc(id_)
        result += f"- **{desc}({id_})** | 가용(Unrestricted): {row['unrestricted_qty']} | 검사중(Inspection): {row['inspection_qty']} | 블로킹(Blocked): {row['blocked_qty']}\n"
    
    if not bs.empty:
        result += "\n#### [배치 상세 내역]\n"
        for _, row in bs.iterrows():
            id_ = str(row['product_id'])
            desc = _get_desc(id_)
            result += f"- {desc}({id_}) | 배치 {row['batch_no']} | 가용 {row['available_qty']} | 만기 {row['expiration_date'].date()} | 입고일 {row['receipt_date'].date()}\n"
            
    return result

@tool
def query_bom(product_id: str):
    """
    특정 자재(product_id)의 BOM(Bill of Materials) 구조를 재귀적으로 조회합니다.
    제품 생산에 필요한 모든 하위 자재 명세와 소요량을 반환합니다.
    """
    data = get_data_loader()
    bom = data.bom.copy()
    product_id = str(product_id)
    
    def get_recursive_bom(pid, level=0):
        comps = bom[bom["root_product_id"] == pid]
        lines = []
        for _, row in comps.iterrows():
            c_id = str(row["component_product_id"])
            qty = row["component_qty"]
            desc = _get_desc(c_id)
            lines.append(f"{'  ' * level}L{level+1}: {desc}({c_id}) [필요량: {qty}]")
            lines.extend(get_recursive_bom(c_id, level + 1))
        return lines

    results = get_recursive_bom(product_id)
    if not results:
        return f"{product_id}에 대한 하위 BOM 정보가 없습니다."
    
    root_desc = _get_desc(product_id)
    return f"### BOM 구성 (Root: {root_desc}({product_id}))\n" + "\n".join(results)

@tool
def query_supply_chain_and_po(product_id: str = None):
    """
    납기 지연 중인 발주 건(PO)과 공급업체(Vendor)의 단가 정보를 조회합니다.
    공급망 리스크 분석이나 구매 단가 파악 시 사용합니다.
    """
    data = get_data_loader()
    po = data.purchase_order.copy()
    vir = data.vendor_into_record.copy()
    
    if product_id:
        product_id = str(product_id)
        po = po[po["product_id"] == product_id]
        vir = vir[vir["product_id"] == product_id]
        
    pending = po[po["schedule_qty"] > po["received_qty"]].copy()
    
    result = "🚚 **발주 진행 현황 (미입고 위주):**\n"
    if pending.empty:
        result += "- 미입고 발주 건이 없습니다.\n"
    else:
        for _, row in pending.iterrows():
            rem = row["schedule_qty"] - row["received_qty"]
            pid = str(row["product_id"])
            desc = _get_desc(pid)
            result += f"- PO {row['po_id']} | 자재 {desc}({pid}) | 잔량 {rem} | 납기 {row['delivery_date'].date()}\n"
            
    result += "\n🏭 **공급업체 단가 현황:**\n"
    for _, row in vir.iterrows():
        pid = str(row["product_id"])
        desc = _get_desc(pid)
        result += f"- {row['vendor_name']} | 자재 {desc}({pid}) | 단가: {row['unit_price']} {row['currency']}\n"
        
    return result

@tool
def query_quality_risk(product_id: str = None):
    """
    부적합(Non-Conformance) 기록 및 보류된 자재 현황을 조회합니다.
    품질 문제로 생산이 불가능한 자재를 식별할 때 사용합니다.
    """
    data = get_data_loader()
    nc = data.non_conformance.copy()
    if product_id:
        nc = nc[nc["product_id"] == str(product_id)]
        
    if nc.empty:
        return "보류 중인 부적합 자재가 없습니다."
        
    result = "🔴 **부적합(NC) 및 보류 현황:**\n"
    for _, row in nc.iterrows():
        pid = str(row["product_id"])
        desc = _get_desc(pid)
        result += f"- 자재 {desc}({pid}) | 배치 {row['batch_no']} | 수량 {row['entry_quantity']} | 사유: {row['movement_type_text']}\n"
    return result

@tool
def query_anomaly_report():
    """
    공급망 전체의 이상 징후(Anomaly)를 스캔하여 종합 리스크 리포트를 생성합니다.
    재고 부족, 만기 임박 배치, 납기 지연 발주(PO), 품질 부적합 항목을 한눈에 파악할 때 사용합니다.
    """
    data = get_data_loader()
    today = pd.Timestamp("2026-03-26")
    results = ["## 🚨 공급망 이상 징후 종합 진단 리포트 (2026-03-26 기준)\n"]
    
    # 1. 재고 부족 (Unrestricted == 0)
    ws = data.warehouse_stock.copy()
    low_stock = ws[ws["unrestricted_qty"] == 0]
    if not low_stock.empty:
        results.append("### 📦 재고 부족 및 품절 위험")
        for _, row in low_stock.iterrows():
            pid = str(row["product_id"])
            desc = _get_desc(pid)
            results.append(f"- **{desc}({pid})**: 가용 재고 없음 (검사중: {row['inspection_qty']})")
        results.append("")

    # 2. 만기 임박 (60일 이내)
    bs = data.batch_stock.copy()
    threshold = today + timedelta(days=60)
    expiring = bs[bs["expiration_date"] <= threshold]
    if not expiring.empty:
        results.append("### ⚠️ 유통기한/만기 임박 배치")
        for _, row in expiring.iterrows():
            pid = str(row["product_id"])
            desc = _get_desc(pid)
            d_day = (row["expiration_date"] - today).days
            results.append(f"- **{desc}({pid})**: 배치 {row['batch_no']} (D-{d_day}, {row['expiration_date'].date()})")
        results.append("")

    # 3. 납기 지연 (delivery_date < today)
    po = data.purchase_order.copy()
    delayed = po[(po["schedule_qty"] > po["received_qty"]) & (po["delivery_date"] < today)]
    if not delayed.empty:
        results.append("### 🚚 납기 지연 발주건")
        for _, row in delayed.iterrows():
            pid = str(row["product_id"])
            desc = _get_desc(pid)
            delay_days = (today - row["delivery_date"]).days
            results.append(f"- **PO {row['po_id']}**: {desc} ({delay_days}일 지연)")
        results.append("")

    # 4. 품질 부적합 (Non-Conformance)
    nc = data.non_conformance.copy()
    if not nc.empty:
        results.append("### 🔴 품질 부적합 및 보류 항목")
        for _, row in nc.iterrows():
            pid = str(row["product_id"])
            desc = _get_desc(pid)
            results.append(f"- **{desc}({pid})**: 배치 {row['batch_no']} ({row['movement_type_text']})")
        results.append("")

    if len(results) == 1:
        return "✅ 현재 탐지된 공급망 이상 징후가 없습니다. 모든 상태가 정상입니다."
        
    return "\n".join(results)

@tool
def search_product_by_name(query_string: str):
    """
    사용자가 입력한 명칭(부분 문자재 이름)과 일치하는 품목 ID와 상호명을 검색합니다.
    자재 ID를 모르거나 모호한 명칭(예: '규석 주사제')을 사용할 때 반드시 이 도구를 먼저 사용하십시오.
    """
    data = get_data_loader()
    query = str(query_string).lower()
    
    # 1) product.csv 검색
    prod_matches = data.product[data.product["description"].str.contains(query, case=False, na=False)].copy()
    
    # 2) prod_plan_code_map.csv 검색
    plan_matches = data.prod_plan_code_map[data.prod_plan_code_map["description"].str.contains(query, case=False, na=False)].copy()
    
    results = {}
    
    for _, row in prod_matches.iterrows():
        pid = str(row["product_id"])
        results[pid] = row["description"]
        
    for _, row in plan_matches.iterrows():
        pid = str(row["product_id"])
        desc = row["description"]
        country = f" ({row['country']})" if pd.notna(row['country']) else ""
        results[pid] = f"{desc}{country}"
        
    if not results:
        return f"'{query_string}'와 일치하는 품목을 찾을 수 없습니다."
        
    output = f"### '{query_string}' 검색 결과 ({len(results)}건):\n"
    for pid, desc in results.items():
        output += f"- **{desc}** (ID: {pid})\n"
        
    output += "\n위 목록 중 질문과 가장 일치하는 ID를 선택하여 후속 분석(재고, BOM 등)을 진행하세요."
    return output

# --- Agent Class ---

class MatAgent:
    def __init__(self, model_name: str = "qwen2.5:32b"):
        self.llm = ChatOllama(model=model_name, temperature=0).bind_tools([
            query_inventory, 
            query_bom, 
            query_supply_chain_and_po,
            query_quality_risk,
            search_product_by_name,
            query_anomaly_report
        ])
        
        # Build Graph
        builder = StateGraph(AgentState)
        
        builder.add_node("agent", self._call_model)
        builder.add_node("tools", ToolNode([
            query_inventory, 
            query_bom, 
            query_supply_chain_and_po, 
            query_quality_risk, 
            search_product_by_name,
            query_anomaly_report
        ]))
        
        builder.set_entry_point("agent")
        builder.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        builder.add_edge("tools", "agent")
        
        self.graph = builder.compile()

    def _should_continue(self, state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "continue"
        return "end"

    def _call_model(self, state: AgentState):
        system_prompt = SystemMessage(content=(
            "너는 원자재 관리 전문가(Digital Colleague)이다. 사용자의 질문 의도를 다음 계층에 따라 분류하여 대응하라:\n\n"
            "1. **전역 조회 및 이상 탐지 (Global Query)**: '전부', '전체', '리스크', '현황 요약' 등의 요청 시, "
            "개별 검색 없이 `query_anomaly_report` 또는 `query_inventory(product_id=None)` 등을 사용하여 전체 시스템 상태를 분석하라.\n"
            "2. **개별 자재 조회 (Entity Query)**: 특정 자재 이름이 명시된 경우, 반드시 먼저 `search_product_by_name` 도구를 사용하여 정확한 ID를 식별한 후 분석을 진행하라.\n"
            "3. **엑셀 리포트 및 버튼 연동**:\n"
            "   - 사용자가 엑셀 생성을 명시적으로 요청하면, 분석 답변 마지막에 `[DOWNLOAD_EXCEL:type]` 태그를 붙여라. (type: inventory, nc, material)\n"
            "   - 상세 내역 조회가 도움이 될 것 같은 일반 분석 답변 뒤에는 `[SUGGEST_EXCEL:type]` 태그를 붙여 사용자에게 제안하라.\n"
            "   - 사용자가 URL을 요청하더라도 절대 텍스트 URL을 직접 주지 말고 반드시 위의 태그 형식으로만 답변하라.\n\n"
            "반드시 제공된 도구를 통해 데이터를 먼저 확인한 후, 비즈니스 인사이트를 포함하여 답변하라. "
            "시스템 기준일은 2026-03-26이다."
        ))
        messages = [system_prompt] + state["messages"]
        response = self.llm.invoke(messages)
        return {"messages": [response]}

    def chat(self, user_input: str):
        config = {"configurable": {"thread_id": "1"}}
        input_message = HumanMessage(content=user_input)
        
        results = []
        for event in self.graph.stream({"messages": [input_message]}, config, stream_mode="values"):
            # We can capture the intermediate steps here for front-end streaming
            results.append(event)
            
        return results[-1]["messages"][-1].content
