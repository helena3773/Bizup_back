from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.database import Base


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    total_cost = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    priority = Column(SQLEnum(OrderPriority), default=OrderPriority.MEDIUM)
    created_at = Column(DateTime, server_default=func.now())

    order = relationship("Order", back_populates="items")


class OrderRecommendation(Base):
    """발주 추천을 위한 계산용 테이블 (뷰 또는 임시 테이블)"""
    __tablename__ = "order_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    current_stock = Column(Float, nullable=False)
    min_stock = Column(Float, nullable=False)
    avg_daily_usage = Column(Float, nullable=False, default=0)
    recommended_quantity = Column(Float, nullable=False)
    priority = Column(SQLEnum(OrderPriority), default=OrderPriority.MEDIUM)
    estimated_cost = Column(Float, nullable=False, default=0)
    days_until_out_of_stock = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())

