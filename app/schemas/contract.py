from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class ContractBase(BaseModel):
    employee_id: int = Field(..., description="직원 ID")
    employer_name: str = Field(..., description="사업체명", max_length=25)
    working_conditions: Optional[str] = Field(None, description="근무조건")
    wage: Optional[str] = Field(None, description="임금")
    contract_date: date = Field(..., description="작성일")
    employee_name: str = Field(..., description="근로자명")
    employee_address: str = Field(..., description="근로자 주소", max_length=50)
    employee_phone: str = Field(..., description="근로자 연락처")
    employee_signature: str = Field(..., description="근로자 서명 (base64 이미지)")


class ContractCreate(ContractBase):
    pass


class ContractUpdate(BaseModel):
    employer_name: Optional[str] = Field(None, description="사업체명", max_length=25)
    working_conditions: Optional[str] = Field(None, description="근무조건")
    wage: Optional[str] = Field(None, description="임금")
    contract_date: Optional[date] = Field(None, description="작성일")
    employee_name: Optional[str] = Field(None, description="근로자명")
    employee_address: Optional[str] = Field(None, description="근로자 주소", max_length=50)
    employee_phone: Optional[str] = Field(None, description="근로자 연락처")
    employee_signature: Optional[str] = Field(None, description="근로자 서명 (base64 이미지)")


class ContractResponse(ContractBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

