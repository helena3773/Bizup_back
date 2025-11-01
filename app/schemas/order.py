from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class OrderPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderRecommendationCreate(BaseModel):
    inventory_item_id: int
    quantity: float
    priority: OrderPriority = OrderPriority.MEDIUM


class OrderRecommendationResponse(BaseModel):
    id: int
    name: str
    current_stock: float
    min_stock: float
    avg_daily: float
    recommended_qty: float
    unit: str
    priority: OrderPriority
    estimated_cost: float
    days_until_out_of_stock: int

    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    inventory_item_id: int = Field(..., description="재고 아이템 ID")
    quantity: float = Field(..., gt=0, description="발주 수량")
    priority: OrderPriority = OrderPriority.MEDIUM


class OrderCreate(BaseModel):
    items: List[OrderItemCreate] = Field(..., description="발주 항목 리스트")


class OrderItemResponse(BaseModel):
    id: int
    name: str
    quantity: float
    unit: str
    unit_price: float
    total_price: float
    priority: OrderPriority

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    status: OrderStatus
    total_cost: float
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

