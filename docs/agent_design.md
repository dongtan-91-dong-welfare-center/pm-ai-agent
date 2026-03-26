# 에이전트 설계 및 ReAct 패턴 (Agent Design & ReAct Pattern)

본 문서는 **MatAgent**의 지능적 의사결정을 담당하는 AI Agent의 설계와 사용되는 ReAct 패턴에 대해 설명합니다.

## 1. 개요 (Overview)

MatAgent는 단순한 챗봇이 아니라, 복잡한 공급망 데이터를 탐색하고 추론할 수 있는 **지능형 디지털 동료(Digital Colleague)**로 설계되었습니다. ReAct (Reason + Act) 패턴을 기반으로 한 LangGraph를 사용하여 일련의 분석 단계를 거쳐 사용자 질문에 답변합니다.

## 2. ReAct 패턴 (Reason + Act Flow)

Agent는 다음과 같은 단계를 반복 수행합니다:

1. **Reasoning (추론)**: 사용자의 질문이 전역 조회인지, 개별 자재 조회인지 분석합니다.
2. **Action (실행)**: 적절한 도구(Tool)를 선택하고 매개변수(Parameter)를 추출하여 호출합니다.
3. **Observation (관찰)**: 호출된 도구에서 반환된 원천 데이터(CSV 결과 등)를 확인합니다.
4. **Conclusion (종결)**: 관찰 결과를 바탕으로 사용자에게 제공할 비즈니스 인사이트를 생성하거나, 추가적인 도구 호출이 필요한지 결정합니다.

## 3. 핵심 도구 세트 (Available Tools)

| 도구명 (Tool Name) | 설명 (Description) | 주요 파라미터 (Parameters) |
| :--- | :--- | :--- |
| `search_product_by_name` | 모호한 명칭으로 자재 ID를 검색합니다. (품목 식별 필수 도구) | `query_string` |
| `query_inventory` | 창고 및 배치별 실물 재고 현황(가용, 검사중, 블로킹)을 조회합니다. | `product_id` (optional) |
| `query_bom` | 특정 제품의 하위 자재 명세(Bill of Materials)를 재귀적으로 조회합니다. | `product_id` |
| `query_supply_chain_and_po` | 발주 현황(PO), 납기 지연, 공급업체 단가 정보를 확인합니다. | `product_id` (optional) |
| `query_quality_risk` | 부적합(Non-Conformance) 기록 및 품질 보류 항목을 조회합니다. | `product_id` (optional) |
| `query_anomaly_report` | 전역 리스크 스캔을 통해 종합 이상 징후 리포트를 생성합니다. | None |

## 4. 계층적 의도 분류 (Hierarchical Intent Classification)

시스템 프롬프트에는 사용자의 의도를 세분화하여 대응하는 로직이 포함되어 있습니다:

### 1단계: 전역 조회 (Global Context)
- '리스크 요약', '전체 상태' 등 광범위한 질문 시, `query_anomaly_report`를 호출하여 전체 공급망을 스캔합니다.

### 2단계: 개별 엔티티 조회 (Entity Context)
- 특정 품명이 언급된 경우, 반드시 `search_product_by_name`으로 ID를 먼저 확인합니다. 
- 예: "규석 주사제 재고 알려줘" -> 1. ID 검색 -> 2. 재고 조회.

### 3단계: 엑셀 리포트 제안 (Contextual Recommendations)
- 분석 결과에 따라 `[DOWNLOAD_EXCEL:...]` 또는 `[SUGGEST_EXCEL:...]` 태그를 부착하여 UI 인터랙션을 유도합니다.

## 5. 지능형 프롬프트 전략 (Prompting Strategy)

- **System Role**: 원자재 관리 전문가(Expert Digital Colleague)로 페르소나를 설정.
- **Strict Logic**: 반드시 도구를 통해 확보된 데이터에 근거하여 답변하도록 강제.
- **Insight Focused**: 단순 데이터 나열이 아닌, "입고 지연이 예상되므로 생산 계획 조정이 필요합니다"와 같은 비즈니스 인사이트 제공.
