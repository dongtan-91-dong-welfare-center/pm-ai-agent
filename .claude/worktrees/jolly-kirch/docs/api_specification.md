# API 명세서 (API Specification)

본 문서는 **MatAgent**의 RESTful 기반 API 통신 인터페이스에 대해 설명합니다.

## 1. 개요 (Overview)

- **Base URL**: `/api/v1` (Default)
- **Content Type**: `application/json`
- **Streaming Support**: 챗 답변을 위한 SSE(Server-Sent Events)를 지원합니다.

## 2. 인터페이스 상세 (Endpoint Details)

### 2.1. 인벤토리 조회 (`GET /api/v1/inventory`)
- **설명**: 현재 창고 재고 및 모델 정보를 결합한 전체 목록을 반환합니다.
- **Request**: 없음
- **Response Example**:
  ```json
  [
    {
      "product_id": "RM001",
      "description": "규석 주사제 100mg",
      "unrestricted_qty": 500.0,
      "inspection_qty": 0.0,
      "blocked_qty": 20.0,
      "base_unit": "ML"
    }
  ]
  ```

### 2.2. AI 에이전트 대화 (`POST /api/v1/chat`)
- **설명**: 사용자와 AI 에이전트 간의 텍스트 대화를 처리합니다.
- **Parameters**:
  - `query` (str): 사용자 질문 내용.
  - `stream` (bool): `true` 로 설정 시 실시간 스트리밍 응답 (StreamingResponse) 제공.
- **Request Body Example**:
  ```json
  {
    "query": "현재 재고 부족한 항목 리스트 보여줘",
    "stream": false
  }
  ```
- **Response Example**:
  ```json
  {
    "response": "현재 '규석 주사제' 등 3개 품목의 가용 재고가 부족합니다. [DOWNLOAD_EXCEL:inventory]"
  }
  ```

### 2.3. 엑셀 리포트 다운로드 (`GET /api/v1/report/excel`)
- **설명**: 특정 데이터셋에 대한 엑셀 파일을 동적으로 생성하여 반환합니다.
- **Query Parameters**:
  - `type` (str): `nc`(부적합), `inventory`(재고), `material`(자재 마스터) 중 선택.
- **Response**: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` 바이너리 스트림.

### 2.4. 긴급 알림 조회 (`GET /api/v1/alerts`)
- **설명**: 현재 시스템 전체의 리스크 요소를 요약하여 반환합니다. (대시보드 노출용)
- **Response Example**:
  ```json
  [
    {
      "type": "STOCK_OUT",
      "message": "자재 'RM002' 가용 재고 0개입니다.",
      "severity": "CRITICAL"
    }
  ]
  ```

## 3. 에러 핸들링 (Error Handling)

- **400 Bad Request**: 유용하지 않은 파라미터 혹은 도구 호출 오류 시 발생.
- **500 Internal Server Error**: LLM 서버 연결 실패 혹은 백엔드 서비스 오류 시 발생.
