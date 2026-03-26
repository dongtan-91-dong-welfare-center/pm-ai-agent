# 🤖 MatAgent: Digital Colleague for Raw Material Management

![GitHub License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python Version](https://img.shields.io/badge/python-3.11%2B-blue) ![Framework](https://img.shields.io/badge/framework-FastAPI%20%2B%20Streamlit-green)

**MatAgent**는 복잡한 원자재 관리 환경에서 의사결정을 지원하는 지능형 AI 에이전트입니다. ReAct(Reason + Act) 패턴을 기반으로 공급망 리스크를 탐지하고, 품질 부적합 항목을 분석하며, 비즈니스 인사이트가 담긴 엑셀 리포트를 실시간으로 제안합니다.

---

## 🌟 주요 기능 (Key Features)

- **🔍 지능형 통합 검색**: 자재 명칭이나 부분 키워드로 정확한 자재 ID와 현황을 식별 (Similarity Search).
- **📦 실시간 재고 & BOM 분석**: 창고별 가용 수량부터 하위 자재 명세(Bill of Materials)까지 계층적 조회.
- **🚨 전역 리스크 스캔**: 납기 지연 발주(PO), 만기 임박 배치, 재고 부족 항목을 한눈에 파악하는 이상 징후 리포트.
- **📊 스마트 엑셀 다운로드**: AI가 분석 내용에 맞춰 필요한 엑셀 리포트(부적합, 재고 등)를 사용자에게 동적으로 제안.
- **🤖 ReAct 기반 추론**: 단순 데이터 조회를 넘어 "가용 재고가 부족하니 생산 스케줄 조정이 필요합니다"와 같은 인사이트 제공.

---

## 🛠 기술 스택 (Tech Stack)

### Frontend
- **Streamlit**: 대화형 UI 및 데이터 시각화.
- **Custom CSS/JS**: 인터랙티브한 엑셀 다운로드 버튼 연동.

### Backend
- **FastAPI**: 효율적이고 빠른 비동기 API 서버.
- **LangGraph**: 복잡한 Agent 상태 관리 및 ReAct 워크플로우 제어.
- **ChatOllama (Qwen 2.5 32B)**: 로컬 LLM 기반 고성능 자연어 추론.
- **Pandas**: 실시간 CSV 데이터 분석 및 조작.

---

## 📂 상세 설계 문서 (Documentation)

더 자세한 설계 내용은 `docs/` 디렉토리의 문서를 참조하십시오:

- [시스템 아키텍처 (Architecture)](docs/architecture.md)
- [에이전트 설계 및 ReAct 패턴 (Agent Design)](docs/agent_design.md)
- [API 명세서 (API Specification)](docs/api_specification.md)
- [데이터 모델 및 원천 데이터 (Data Model)](docs/data_model.md)
- [실행 가이드라인 (Operation Guideline)](docs/operation_guide.md)

---

## 🚀 빠른 시작 (Getting Started)

### 1. 환경 설정
```bash
# 가상 환경 생성 및 진입
python -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install -r backend/requirements.txt
```

### 2. 로컬 LLM 실행 (Ollama)
```bash
# Ollama 설치 후 모델 실행
ollama run qwen2.5:32b
```

### 3. 서비스 실행
- **Backend**: `cd backend && uvicorn main:app --reload --port 8000`
- **Frontend**: `cd frontend && streamlit run app.py --server.port 8501`

---

## 📸 스크린샷 (Screenshots)

*(여기에 대시보드 및 채팅 인터페이스 스크린샷을 추가할 수 있습니다)*

---

## 📝 라이선스 (License)

Copyright © 2026 MatAgent Project. Licensed under the [MIT License](LICENSE).
