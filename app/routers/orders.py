from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.order import OrderRecommendationResponse, OrderCreate, OrderResponse
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["발주 관리"])


@router.get("/recommendations", response_model=List[OrderRecommendationResponse])
def get_order_recommendations(db: Session = Depends(get_db)):
    recommendations = order_service.get_order_recommendations(db)
    
    result = []
    for rec in recommendations:
        result.append(OrderRecommendationResponse(
            id=rec["id"],
            name=rec["name"],
            current_stock=rec["current_stock"],
            min_stock=rec["min_stock"],
            avg_daily=rec["avg_daily"],
            recommended_qty=rec["recommended_qty"],
            unit=rec["unit"],
            priority=rec["priority"],
            estimated_cost=rec["estimated_cost"],
            days_until_out_of_stock=rec["days_until_out_of_stock"]
        ))
    
    return result


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    return order_service.create_order(db, order)

