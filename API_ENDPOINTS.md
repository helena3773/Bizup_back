# API 엔드포인트 문서

## 기본 정보
- **Base URL**: `http://localhost:8000/api/v1`
- **API 문서**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc**: `http://localhost:8000/redoc`

---

## 재고 관리 (Inventory)

### 재고 목록 조회
```
GET /api/v1/inventory
```
**쿼리 파라미터**:
- `skip`: int (기본값: 0) - 건너뛸 항목 수
- `limit`: int (기본값: 100, 최대: 1000) - 조회할 항목 수
- `search`: string (선택) - 검색어 (상품명 또는 카테고리)

**응답 예시**:
```json
[
  {
    "id": 1,
    "name": "생수 500ml",
    "category": "음료",
    "quantity": 120,
    "unit": "개",
    "min_quantity": 50,
    "price": 500,
    "last_updated": "2025-10-09",
    "created_at": "2025-10-09T10:00:00",
    "updated_at": "2025-10-09T10:00:00",
    "status": "정상"
  }
]
```

### 재고 통계
```
GET /api/v1/inventory/stats
```

### 재고 부족 목록
```
GET /api/v1/inventory/low-stock
```

### 특정 재고 조회
```
GET /api/v1/inventory/{item_id}
```

### 재고 추가
```
POST /api/v1/inventory
```
**요청 본문**:
```json
{
  "name": "새 상품",
  "category": "음료",
  "quantity": 100,
  "unit": "개",
  "min_quantity": 50,
  "price": 1000
}
```

### 재고 수정
```
PUT /api/v1/inventory/{item_id}
```
**요청 본문** (모든 필드 선택):
```json
{
  "quantity": 150,
  "price": 1200
}
```

### 재고 삭제
```
DELETE /api/v1/inventory/{item_id}
```

---

## 발주 관리 (Orders)

### 발주 추천 목록
```
GET /api/v1/orders/recommendations
```
**응답 예시**:
```json
[
  {
    "id": 1,
    "name": "우유",
    "current_stock": 8,
    "min_stock": 15,
    "avg_daily": 5,
    "recommended_qty": 20,
    "unit": "L",
    "priority": "high",
    "estimated_cost": 60000,
    "days_until_out_of_stock": 2
  }
]
```

### 발주 생성
```
POST /api/v1/orders
```
**요청 본문**:
```json
{
  "items": [
    {
      "inventory_item_id": 1,
      "quantity": 20,
      "priority": "high"
    },
    {
      "inventory_item_id": 2,
      "quantity": 10,
      "priority": "medium"
    }
  ]
}
```

---

## 품절 관리 (Out of Stock)

### 품절 상품 목록
```
GET /api/v1/out-of-stock
```
**응답 예시**:
```json
[
  {
    "id": 1,
    "name": "딸기 시럽",
    "category": "식재료",
    "days_out_of_stock": 5,
    "last_stock": 3,
    "unit": "L",
    "estimated_loss": 150000,
    "status": "critical"
  }
]
```

### 재입고 완료 처리
```
POST /api/v1/out-of-stock/{item_id}/restock
```
**쿼리 파라미터**:
- `quantity`: float - 재입고 수량

**예시**: `POST /api/v1/out-of-stock/1/restock?quantity=50`

---

## 직원 관리 (Employees)

### 직원 목록 조회
```
GET /api/v1/employees
```

### 특정 직원 조회
```
GET /api/v1/employees/{employee_id}
```

### 직원 추가
```
POST /api/v1/employees
```
**요청 본문**:
```json
{
  "name": "홍길동",
  "role": "매니저",
  "phone": "010-1234-5678",
  "join_date": "2025-01-01"
}
```

### 직원 정보 수정
```
PUT /api/v1/employees/{employee_id}
```
**요청 본문** (모든 필드 선택):
```json
{
  "name": "홍길동",
  "role": "매니저",
  "phone": "010-9876-5432",
  "status": "active"
}
```

### 직원 삭제
```
DELETE /api/v1/employees/{employee_id}
```

---

## 가게 설정 (Store)

### 가게 정보 조회
```
GET /api/v1/store
```

### 가게 정보 업데이트
```
PUT /api/v1/store
```
**요청 본문**:
```json
{
  "name": "우리 카페",
  "address": "서울시 강남구 테헤란로 123",
  "phone": "02-1234-5678"
}
```

### 알림 설정 조회
```
GET /api/v1/store/notifications
```

### 알림 설정 업데이트
```
PUT /api/v1/store/notifications
```
**요청 본문**:
```json
{
  "low_stock": true,
  "out_of_stock": true,
  "order_reminder": true,
  "daily_report": false
}
```

---

## 공통

### 루트 엔드포인트
```
GET /
```

### 헬스 체크
```
GET /health
```

