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
- `limit`: int (기본값: 1000, 최대: 10000) - 조회할 항목 수
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

### 재고 수정
```
PUT /api/v1/inventory/{item_id}
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
**응답**: 201 Created

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

## 메뉴 관리 (Menus)

### 메뉴 CSV 업로드 (추가/초기화)
```
POST /api/v1/menus/upload-csv?mode={add|reset}
```
- **mode**  
  - `add` (기본값): 기존 메뉴는 유지하고, 동일한 이름의 메뉴는 재료 정보를 갱신하거나 추가합니다.  
  - `reset`: 기존 메뉴/재료/재고를 모두 삭제한 뒤 업로드한 CSV 기준으로 완전히 재구성합니다.
- **요청**: `multipart/form-data`, 필수 필드 `file`

**응답 예시 (성공)**:
```json
{
  "success": true,
  "mode": "add",
  "message": "[추가] 12개 메뉴 데이터를 처리했습니다. (신규 4개, 업데이트 8개)",
  "menus_count": 12,
  "menus_created": 4,
  "menus_updated": 8,
  "ingredients_registered": 25,
  "ingredient_names": ["물", "에스프레소샷", "..."],
  "total_inventory_count": 58,
  "ingredient_inventory_count": 34,
  "menus": [
    {
      "id": 1,
      "name": "아메리카노",
      "ingredients": [
        {
          "ingredient_name": "물",
          "quantity": 200,
          "unit": "ml"
        }
      ]
    }
  ]
}
```

**응답 예시 (실패)**:
```json
{
  "success": false,
  "mode": "reset",
  "message": "CSV 파싱 오류 ..."
}
```

### 메뉴 목록 조회
```
GET /api/v1/menus
```
**응답**: 메뉴 이름과 재료 목록만 포함됩니다.
```json
[
  {
    "id": 1,
    "name": "아이스 라떼",
    "ingredients": [
      { "ingredient_name": "에스프레소샷", "quantity": 2, "unit": "shot" },
      { "ingredient_name": "우유", "quantity": 180, "unit": "ml" },
      { "ingredient_name": "얼음", "quantity": 150, "unit": "g" }
    ]
  }
]
```

---

## 매출 관리 (Sales)

### 매출 데이터 수신
```
POST /api/v1/sales/receive
```
**요청 본문**:
```json
{
  "sales": [
    {
      "menu_name": "아이스 라떼",
      "quantity": 3,
      "timestamp": "2025-10-09T12:34:56"
    },
    {
      "menu_name": "크림 파스타",
      "quantity": 1,
      "timestamp": "2025-10-09T12:35:02"
    }
  ]
}
```
서버는 각 메뉴에 매핑된 재료 기준으로 재고를 자동 차감하고, 부족/품절 상태 변화가 있으면 경고 메시지를 포함한 결과를 반환합니다.

**응답 예시**:
```json
{
  "results": [
    {
      "menu_name": "아이스 라떼",
      "quantity": 3,
      "status": "success",
      "deducted_items": [
        {
          "ingredient": "우유",
          "deducted": 540,
          "remaining": 1260,
          "status": "정상",
          "status_changed": false
        },
        {
          "ingredient": "얼음",
          "deducted": 450,
          "remaining": 50,
          "status": "부족",
          "status_changed": true,
          "warning": "얼음 재고가 부족합니다!"
        }
      ]
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
**쿼리 파라미터** (필수):
- `quantity`: float (필수, > 0) - 재입고 수량

**예시**: 
```
POST /api/v1/out-of-stock/1/restock?quantity=50
```

**응답 예시**:
```json
{
  "message": "재입고가 완료되었습니다",
  "item": {
    "id": 1,
    "name": "딸기 시럽",
    "category": "식재료",
    "quantity": 50,
    "unit": "L",
    "min_quantity": 10,
    "price": 5000,
    "last_updated": "2025-10-09",
    "created_at": "2025-10-09T10:00:00",
    "updated_at": "2025-10-09T15:00:00"
  }
}
```

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
**응답**: 201 Created

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
**응답**: 200 OK

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
**응답**: 204 No Content

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
**응답**: 200 OK

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
**응답**: 200 OK

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

### 헬스 체크 (서버 상태 확인)
```
GET /health
```

