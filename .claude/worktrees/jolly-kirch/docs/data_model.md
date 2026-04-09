# 데이터 모델 및 원천 데이터 (Data Model & Source Data)

본 문서는 **MatAgent**에서 사용하는 원천 데이터(CSV)의 구조와 영속성 데이터베이스(SQLite)의 스키마에 대해 설명합니다.

## 1. 정적/동적 원천 데이터 (CSV Files)

백엔드 `backend/app/data/` 하위의 CSV 파일들은 시스템의 주요 비즈니스 데이터를 담고 있습니다. 주요 파일 구조는 다음과 같습니다:

### 1.1. 자재 및 품목 (Material & Product)
- **`product.csv`**: 기본 품목 마스터 (ID, 명칭, 단위 등)
- **`prod_plan_code_map.csv`**: 생산 계획 코드와 실제 품목 ID 간의 매핑 정보.

### 1.2. 재고 현황 (Stock Status)
- **`warehouse_stock.csv`**: 창고별 요약 재고 (가용, 검사중, 블로킹 수량)
- **`batch_stock.csv`**: 배치 단위의 상세 재고 (입고일, 만기일, 배치번호)

### 1.3. 공급망 및 품질 (Supply Chain & Quality)
- **`purchase_order.csv`**: 발주 현황 (PO 번호, 발주량, 입고량, 납기일)
- **`vendor_into_record.csv`**: 공급업체(Vendor) 단가 및 자재 정보.
- **`non_conformance.csv`**: 품질 부적합(NC) 및 보류 사유 기록.

### 1.4. 구조 및 계획 (Structure & Plan)
- **`bom.csv`**: Bill of Materials (상위 자재 - 하위 자재 간 소요량 및 계층)
- **`production_plan.csv`**: 생산 계획 (일자별 필요 수량)

## 2. 영속성 데이터 (SQLite DB)

감사 로그 및 사용자 설정 등은 `raw_material_agent.db`에 저장됩니다. (SQLModel 기반)

### 2.1. AuditLog 테이블
- **설명**: 사용자의 질문 및 AI 답변에 대한 기록을 보관합니다.
- **주요 필드**:
  - `id`: 고유 ID (Private Key)
  - `user_id`: 사용자 식별자
  - `action`: 수행 작업 (CHAT, DOWNLOAD_EXCEL 등)
  - `details`: 대화 내용 요약 혹은 상세 로그
  - `timestamp`: 발생 일시

## 3. 데이터 로드 로직 (Data Loader)

시스템은 `backend/app/core/data_loader.py`를 통해 모든 CSV 데이터를 인메모리 Pandas DataFrame으로 로드합니다.
- **특징**: 데이터 로드 시 날짜 컬럼(`expiration_date`, `delivery_date` 등)은 자동으로 `datetime` 객체로 변환되어 ReAct Agent의 날짜 기반 추론(만기 D-Day 계산 등)을 지원합니다.
