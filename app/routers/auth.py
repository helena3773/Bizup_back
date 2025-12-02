from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import settings


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


router = APIRouter(prefix="/auth", tags=["인증"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    if (
        payload.username != settings.ADMIN_USERNAME
        or payload.password != settings.ADMIN_PASSWORD
    ):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")

    # 데모용 단순 토큰큰
    token = f"bizup-token-{payload.username}"
    return LoginResponse(access_token=token, username=payload.username)


