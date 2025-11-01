from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum


class EmployeeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class EmployeeBase(BaseModel):
    name: str = Field(..., description="이름")
    role: str = Field(..., description="직책")
    phone: str = Field(..., description="전화번호")


class EmployeeCreate(EmployeeBase):
    join_date: date = Field(default_factory=lambda: date.today(), description="입사일")


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[EmployeeStatus] = None


class EmployeeResponse(EmployeeBase):
    id: int
    status: EmployeeStatus
    join_date: date
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

