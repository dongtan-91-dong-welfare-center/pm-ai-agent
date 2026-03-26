# 실행 가이드라인 (Operation Guideline)

본 문서는 **MatAgent** 프로젝트를 로컬 환경에서 설치하고 실행하기 위한 상세 절차를 설명합니다.

## 1. 사전 요구 사항 (Prerequisites)

- **Python**: 3.11 버전 이상 권장
- **Ollama**: 로컬 LLM 서버 (설치: [ollama.com](https://ollama.com))
- **Git** (소스 코드 관리용)

## 2. LLM 서버 설정 (Ollama Setup)

MatAgent는 고성능 추론을 위해 `qwen2.5:32b` 모델을 기본으로 사용합니다.

1. Ollama를 실행합니다.
2. 터미널에서 다음 명령어를 입력하여 모델을 내려받습니다:
   ```bash
   ollama pull qwen2.5:32b
   ```
   *참고: 메모리 사양이 부족할 경우 `qwen2.5:7b`나 `llama3.1:8b`로 `llm_agent.py` 코드를 수정하여 사용할 수 있습니다.*

## 3. 백엔드 설치 및 실행 (Backend Setup)

1. **가상 환경 생성 및 활성화**:
   ```bash
   # 프로젝트 루트 디렉토리에서 실행
   python -m venv .venv
   source .venv/bin/activate  # MacOS/Linux
   # .venv\Scripts\activate   # Windows
   ```

2. **의존성 설치**:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **백엔드 서버 실행**:
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```
   *정상 실행 시 http://localhost:8000/docs 에서 API 문서를 확인할 수 있습니다.*

## 4. 프론트엔드 설치 및 실행 (Frontend Setup)

프론트엔드는 Streamlit을 사용하여 구현되었습니다.

1. **새로운 터미널**을 열고 가상 환경을 활성화합니다.
2. **프론트엔드 실행**:
   ```bash
   cd frontend
   streamlit run app.py --server.port 8501
   ```
   *정상 실행 시 브라우저가 자동으로 열리며 http://localhost:8501 에 접속됩니다.*

## 5. 데이터 준비 (Data Verification)

백엔드 실행 시 `backend/data/` 디렉토리에 다음 CSV 파일들이 존재하는지 확인하십시오:
- `product.csv`, `warehouse_stock.csv`, `batch_stock.csv`, `bom.csv` 등 (총 14개 파일)
- 파일이 없을 경우 `data_loader.py`에서 에러가 발생할 수 있습니다.

## 6. 문제 해결 (Troubleshooting)

| 현상 | 원인 | 해결 방법 |
| :--- | :--- | :--- |
| `ConnectionError` (Ollama) | Ollama 서비스가 꺼져 있음 | Ollama 앱을 실행하거나 `ollama serve` 명령 수행 |
| `File Not Found` (CSV) | 경로 설정 오류 | `backend/` 디렉토리 내에서 uvicorn을 실행했는지 확인 |
| API 호출 실패 | 포트 충돌 | 8000번 혹은 8501번 포트가 사용 중인지 확인 후 프로세스 종료 |

## 7. 테스트 방법 (Testing)

실행 후 채팅창에 다음과 같이 입력하여 정상 작동 여부를 확인하십시오:
- *"전체 리스크 현황 리포트 생성해줘"*
- *"규석 주사제 재고 확인해줘"*
