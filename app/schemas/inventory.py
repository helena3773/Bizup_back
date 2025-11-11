from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class InventoryItemBase(BaseModel):
    name: str = Field(..., description="상품명")
    category: str = Field(..., description="카테고리")
    quantity: float = Field(..., ge=0, description="현재 수량")
    unit: str = Field(..., description="단위")
    min_quantity: float = Field(..., ge=0, description="최소 수량")
    price: float = Field(..., ge=0, description="단가")


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = None
    min_quantity: Optional[float] = Field(None, ge=0)
    price: Optional[float] = Field(None, ge=0)


class InventoryItemResponse(InventoryItemBase):
    id: int
    last_updated: date
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StockStatus(str):
    NORMAL = "정상"
    LOW = "부족"
    OUT_OF_STOCK = "품절"


class InventoryItemWithStatus(InventoryItemResponse):
    status: str = Field(..., description="재고 상태: 정상/부족/품절")

