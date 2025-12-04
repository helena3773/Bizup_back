from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class StoreBase(BaseModel):
    name: str = Field(..., description="가게 이름")
    address: Optional[str] = Field(None, description="주소")
    phone: Optional[str] = Field(None, description="전화번호")


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None


class StoreResponse(StoreBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationSettingsBase(BaseModel):
    low_stock: bool = Field(True, description="재고 부족 알림")
    out_of_stock: bool = Field(True, description="품절 알림")
    order_reminder: bool = Field(True, description="발주 알림")
    daily_report: bool = Field(False, description="일일 리포트")


class NotificationSettingsUpdate(NotificationSettingsBase):
    pass


class NotificationSettingsResponse(NotificationSettingsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OutOfStockItemResponse(BaseModel):
    id: int
    name: str
    category: str
    days_out_of_stock: int
    last_stock: float
    unit: str
    estimated_loss: float
    status: str

    class Config:
        from_attributes = True


class OutOfStockMenuResponse(BaseModel):
    id: int
    name: str
    missing_ingredients: List[str]
    days_out_of_stock: int
    status: str

    class Config:
        from_attributes = True
