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
- 재고/메뉴 관리 탭에서 CSV를 업로드해 백엔드에 메뉴가 등록되어 있다면, 시뮬레이터는 별도 작업 없이 그 데이터를 자동으로 감지해 사용
- 실행 중에도 주기적으로 메뉴를 다시 불러오기 때문에 새로운 CSV 업로드가 발생하면 바로 반영
- 백엔드에 메뉴가 비어 있을 때만 기본 CSV(`back/dummy_data/small_file.csv`)를 자동으로 업로드해 초기 데이터를 구성합 (이 파일이 없다면 `dummy_data` 폴더 내 다른 CSV를 무작위로 선택)
- `python sales_simulator.py --csv "경로/파일명.csv"` 형태로 실행하면,
  - 절대 경로, 상대 경로, `back/dummy_data` 폴더 모두 자동 탐색
  - 지정한 CSV를 백엔드에 업로드한 뒤 해당 메뉴 구성을 기준으로 매출 시뮬레이션을 진행하며, 기존 메뉴가 있더라도 이 파일로 다시 초기화