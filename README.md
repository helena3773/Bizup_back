# BIZUP 백엔드 API

가게 운영 관리 시스템을 위한 FastAPI 백엔드 서버입니다.

## 프로젝트 구조

```
back/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 애플리케이션 진입점
│   ├── config.py            # 설정 관리
│   ├── database.py          # 데이터베이스 연결
│   ├── models/              # SQLAlchemy 모델
│   │   ├── __init__.py
│   │   ├── inventory.py     # 재고 모델
│   │   ├── order.py         # 발주 모델
│   │   ├── employee.py      # 직원 모델
│   │   ├── store.py         # 가게 설정 모델
│   │   └── menu.py          # 메뉴 모델 (신규)
│   ├── schemas/             # Pydantic 스키마
│   │   ├── __init__.py
│   │   ├── inventory.py
│   │   ├── order.py
│   │   ├── employee.py
│   │   ├── store.py
│   │   └── menu.py          # 메뉴 스키마 (신규)
│   ├── routers/             # API 라우터
│   │   ├── __init__.py
│   │   ├── inventory.py     # 재고 관리 API
│   │   ├── orders.py        # 발주 추천 API
│   │   ├── outofstock.py    # 품절 관리 API
│   │   ├── employees.py     # 직원 관리 API
│   │   ├── store.py         # 가게 설정 API
│   │   ├── menus.py         # 메뉴 관리 API (신규)
│   │   └── sales.py         # 매출 관리 API (신규)
│   └── services/            # 비즈니스 로직
│       ├── __init__.py
│       ├── inventory_service.py
│       ├── order_service.py
│       ├── analytics_service.py
│       └── menu_service.py  # 메뉴 서비스 (신규)
├── sales_simulator.py       # 가상 매출 시뮬레이터 (신규)
├── requirements.txt         # Python 패키지 의존성
└── bizupenv/                # 환경 변수 (생성 필요)
```

## 설치 및 실행

1. 의존성 설치 (venv 활성화하고 설치하기!):
```bash
pip install -r requirements.txt
```

2. 환경 변수 설정 (.env 파일 생성):
```
DATABASE_URL=sqlite:미정
SECRET_KEY=미정
```

3. 서버 실행:
```bash
uvicorn app.main:app --reload
```

API 문서는 `http://localhost:8000/docs`에서 확인할 수 있습니다.

## 새로운 기능

### 가상 매출 API 시스템

CSV 파일로 메뉴를 등록하고, 가상 매출 시뮬레이터를 통해 실시간 재고 관리를 할 수 있습니다.

주요 기능:
- CSV 파일을 통한 메뉴 등록
- 가상 매출 시뮬레이터 (주기적 매출 생성)
- 실시간 재고 자동 차감

빠른 시작:
1. 백엔드 서버 실행: `uvicorn app.main:app --reload`
2. CSV 파일 업로드: 프로그램 '메뉴 관리' 탭에서 직접
3. 시뮬레이터 실행: `python sales_simulator.py`

#### 사용자 CSV 기반 시뮬레이션
- 재고 탭에서 사용한 동일한 CSV 파일을 시뮬레이터에서도 그대로 사용 (이미 CSV를 업로드했다면 --csv 옵션 없이 실행)
- `python sales_simulator.py --csv "경로/파일명.csv"` 형태로 실행하면,
  - 절대 경로, 상대 경로, `back/dummy_data` 폴더 모두 자동 탐색
  - 지정한 CSV를 백엔드에 업로드한 뒤 해당 메뉴 구성을 기준으로 매출 시뮬레이션을 진행
- `dummy_data` 폴더에 있는 기본 CSV를 쓰고 싶다면 `--csv` 옵션 없이 실행