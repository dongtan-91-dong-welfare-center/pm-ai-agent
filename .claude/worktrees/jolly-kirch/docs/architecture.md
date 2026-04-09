# 시스템 아키텍처 (System Architecture)

본 문서는 **MatAgent (Raw Material Management AI Agent)**의 전체 시스템 구성 및 데이터 흐름에 대해 설명합니다.

## 1. 개요 (Overview)

MatAgent는 공급망(Supply Chain) 및 원자재(Raw Material) 데이터를 분석하여 사용자에게 인사이트를 제공하는 **Digital Colleague**입니다. ReAct 패턴과 LangGraph를 활용하여 자재 부족, 품질 리스크, 납기 지연 등의 복합적인 상황을 지능적으로 탐지하고 대응합니다.

## 2. 레이어 아키텍처 (Layered Architecture)

시스템은 크게 3개의 레이어로 구성됩니다:

### 2.1. Presentation Layer (Streamlit)
- **기술**: Streamlit (Python-based Web Framework)
- **역할**: 사용자 대화 인터페이스, 실시간 AI 응답 렌더링, 엑셀 리포트 다운로드 연동, 알림 대시보드.
- **특징**: `[DOWNLOAD_EXCEL:...]` 등의 특수 태그를 파싱하여 UI 버튼을 동적으로 생성.

### 2.2. Application & API Layer (FastAPI)
- **기술**: FastAPI (Asynchronous Python Web Framework)
- **역할**: 비즈니스 로직 처리, AI Agent 서비스 실행, 데이터 로더 관리, 감사 로그 기록.
- **주요 엔드포인트**:
  - `/chat`: AI 에이전트와의 실시간 스트리밍 대화.
  - `/inventory`: 현재 자재 재고 현황 조회.
  - `/report/excel`: 동적 엑셀 리포트 생성 및 다운로드.
  - `/alerts`: 요약된 리스크 알림 정보 제공.

### 2.3. Data & AI Engine Layer (LangGraph & Ollama)
- **기술**: LangGraph (State Graph Management), ChatOllama (Local LLM), SQLite (Audit Logging).
- **역할**: LLM 기반 추론 및 도구(Tools) 호출, 데이터베이스(CSV 및 SQL) 정보 추출.
- **핵심 로직**:
  - `llm_agent.py`: LangGraph를 이용한 ReAct 패턴 구현.
  - `data_loader.py`: CSV 파일 기반의 인메모리 데이터 연동.

## 3. 데이터 흐름 (Data Flow)

1. **User Request**: 사용자가 Streamlit UI에서 질문을 입력합니다.
2. **FastAPI Proxy**: 요청이 백엔드 `/chat` 엔드포인트로 전달됩니다.
3. **Agent Loop (ReAct)**:
   - LLM이 질문을 분석하여 어떤 도구(Tool)를 사용할지 결정합니다.
   - `search_product_by_name`, `query_inventory` 등 정의된 도구를 순차적/재귀적으로 호출합니다.
   - 도구 실행 결과(Observation)를 바탕으로 최종 답변을 생성합니다.
4. **Response Generation**: 생성된 답변과 함께 엑셀 다운로드 추천 태그를 포함하여 반환합니다.
5. **Observation**: 답변의 내용을 바탕으로 사용자가 엑셀 리포트를 클릭하면 백엔드에서 실시간으로 엑셀을 생성하여 제공합니다.

## 4. 시스템 배계 (System Environment)

- **OS**: Local (MacOS/Linux recommended)
- **Backend Model**: Ollama (Qwen 2.5 32B 권장)
- **Database**: 
  - 정적 정보: CSV files (.csv)
  - 감사 로그: SQLite (raw_material_agent.db)
