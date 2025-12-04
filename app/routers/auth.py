from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str | None = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


class RegisterResponse(BaseModel):
    message: str
    username: str


router = APIRouter(prefix="/auth", tags=["인증"])


@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == payload.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")
    
    new_user = User(
        username=payload.username,
        password=payload.password,  # 실제 운영에서는 bcrypt 등으로 해시 필요
        email=payload.email,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return RegisterResponse(
        message="회원가입이 완료되었습니다.",
        username=new_user.username
    )


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    if (
        payload.username == settings.ADMIN_USERNAME
        and payload.password == settings.ADMIN_PASSWORD
    ):
        token = f"bizup-token-{payload.username}"
        return LoginResponse(access_token=token, username=payload.username)
    
    # 일반 사용자 계정 체크
    user = db.query(User).filter(User.username == payload.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="비활성화된 계정입니다.")
    
    # 실제 운영에서는 비밀번호 해시 비교 필요 (현재는 평문 비교)
    if user.password != payload.password:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")
    
    token = f"bizup-token-{user.username}"
    return LoginResponse(access_token=token, username=user.username)


