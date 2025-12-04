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
   - `back/.env.example` 파일을 참고하여 `back/.env` 파일을 생성하세요.
   - 또는 다음 내용으로 `.env` 파일을 생성:
   ```
   DATABASE_URL=sqlite:///./data/bizup.db
   SECRET_KEY=your-secret-key-change-this-in-production
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=bizup1234
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
- 백엔드에 메뉴가 비어 있을 때만 기본 CSV(`back/dummy_data/small_file.csv`)를 자동으로 업로드해 초기 데이터를 구성 (이 파일이 없다면 `dummy_data` 폴더 내 다른 CSV를 무작위로 선택)
- `python sales_simulator.py --csv "경로/파일명.csv"` 형태로 실행하면,
  - 절대 경로, 상대 경로, `back/dummy_data` 폴더 모두 자동 탐색
  - 지정한 CSV를 백엔드에 업로드한 뒤 해당 메뉴 구성을 기준으로 매출 시뮬레이션을 진행하며, 기존 메뉴가 있더라도 이 파일로 다시 초기화

## 서버 배포 가이드

### 데이터베이스 설정 (중요!)

이 프로젝트는 SQLite 데이터베이스를 사용하며, 데이터는 `data/` 디렉토리에 저장됩니다. 
서버 배포 시 데이터 손실을 방지하기 위해 다음 단계를 따르세요:

#### 1. 로컬에서 기존 데이터베이스 파일 이동

기존 `bizup.db` 파일이 있다면 `data/` 디렉토리로 이동:

```bash
# back 디렉토리에서 실행
mkdir -p data
mv bizup.db data/bizup.db  # Windows: move bizup.db data\bizup.db
```

#### 2. 서버 배포 준비

1. **환경 변수 파일 생성**
   - 서버의 `back/` 디렉토리에 `.env` 파일 생성
   - `.env.example` 파일을 참고하여 작성
   - 또는 다음 내용으로 생성:
   ```env
   DATABASE_URL=sqlite:///./data/bizup.db
   SECRET_KEY=your-secret-key-change-this-in-production
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=bizup1234
   ```

2. **데이터 디렉토리 생성 및 권한 설정** (Linux/Mac)
   ```bash
   mkdir -p data
   chmod 755 data
   ```

3. **기존 데이터베이스 파일 복사** (첫 배포가 아닌 경우)
   - 로컬의 `back/data/bizup.db` 파일을 서버의 `back/data/` 디렉토리로 복사
   - 또는 서버에서 직접 데이터베이스 파일을 생성한 경우, 해당 파일을 유지

#### 3. 서버에서 실행

```bash
# 가상환경 활성화 (필요한 경우)
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows

# 서버 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 4. 데이터베이스 백업 (권장)

정기적으로 `data/bizup.db` 파일을 백업하세요:

```bash
# 백업
cp data/bizup.db data/bizup.db.backup

# 복원 (필요한 경우)
cp data/bizup.db.backup data/bizup.db
```

### 주의사항

- **데이터 디렉토리**: `data/` 디렉토리는 Git에 커밋되지 않습니다 (`.gitignore`에 포함)
- **환경 변수**: `.env` 파일도 Git에 커밋되지 않으므로, 서버에서 별도로 생성해야 합니다
- **데이터 보존**: 서버 재시작 시에도 `data/bizup.db` 파일이 유지되므로 회원 정보가 사라지지 않습니다
- **절대 경로 사용**: 필요시 `.env`에서 절대 경로 사용 가능
  - Linux: `DATABASE_URL=sqlite:////var/lib/bizup/bizup.db`
  - Windows: `DATABASE_URL=sqlite:///C:/data/bizup.db`