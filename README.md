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
│   │   └── store.py         # 가게 설정 모델
│   ├── schemas/             # Pydantic 스키마
│   │   ├── __init__.py
│   │   ├── inventory.py
│   │   ├── order.py
│   │   ├── employee.py
│   │   └── store.py
│   ├── routers/             # API 라우터
│   │   ├── __init__.py
│   │   ├── inventory.py     # 재고 관리 API
│   │   ├── orders.py        # 발주 추천 API
│   │   ├── outofstock.py    # 품절 관리 API
│   │   ├── employees.py     # 직원 관리 API
│   │   └── store.py         # 가게 설정 API
│   └── services/            # 비즈니스 로직
│       ├── __init__.py
│       ├── inventory_service.py
│       ├── order_service.py
│       └── analytics_service.py
├── requirements.txt         # Python 패키지 의존성
└── .env                     # 환경 변수 (생성 필요)
```

## 설치 및 실행

1. 의존성 설치:
```bash
pip install -r requirements.txt
```

2. 환경 변수 설정 (.env 파일 생성):
```
DATABASE_URL=sqlite:///./bizup.db
SECRET_KEY=your-secret-key-here
```

3. 서버 실행:
```bash
uvicorn app.main:app --reload
```

API 문서는 `http://localhost:8000/docs`에서 확인할 수 있습니다.

