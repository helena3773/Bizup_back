from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.inventory import InventoryItem
from app.models.order import Order, OrderItem, OrderPriority
from app.schemas.order import OrderCreate
from typing import List, Dict


def calculate_avg_daily_usage(inventory_item: InventoryItem, days: int = 7) -> float:
    """일평균 사용량 계산 (예시: 실제로는 판매 기록을 기반으로 계산)"""
    # TODO: 실제 판매 데이터를 기반으로 계산하도록 수정
    # 현재는 재고와 최소 재고를 기반으로 추정
    if inventory_item.quantity == 0:
        return 1.0  # 품절된 경우 기본값
    
    # 간단한 추정: 현재 재고가 최소 재고 대비 얼마나 있는지로 계산
    estimated_usage = max(0.5, inventory_item.min_quantity / 30.0)  # 월간 최소재고량 기준
    return estimated_usage


def calculate_days_until_out_of_stock(current_stock: float, avg_daily: float) -> int:
    """품절까지 예상 일수 계산"""
    if avg_daily <= 0:
        return 999  # 무제한
    return int(current_stock / avg_daily)


def calculate_recommended_quantity(
    current_stock: float,
    min_stock: float,
    avg_daily: float,
    days_buffer: int = 7
) -> float:
    """권장 발주량 계산"""
    # 필요한 최소 재고량 + 버퍼 기간 동안의 사용량
    needed_stock = min_stock + (avg_daily * days_buffer)
    recommended = needed_stock - current_stock
    return max(0, recommended)


def determine_priority(days_until_out: int) -> OrderPriority:
    """우선순위 결정"""
    if days_until_out <= 2:
        return OrderPriority.HIGH
    elif days_until_out <= 5:
        return OrderPriority.MEDIUM
    else:
        return OrderPriority.LOW


def get_order_recommendations(db: Session) -> List[Dict]:
    """발주 추천 목록 조회"""
    inventory_items = db.query(InventoryItem).all()
    recommendations = []
    
    for item in inventory_items:
        avg_daily = calculate_avg_daily_usage(item)
        days_until_out = calculate_days_until_out_of_stock(item.quantity, avg_daily)
        
        # 재고가 부족하거나 곧 부족할 예정인 경우만 추천
        if item.quantity <= item.min_quantity or days_until_out <= 7:
            recommended_qty = calculate_recommended_quantity(
                item.quantity,
                item.min_quantity,
                avg_daily
            )
            
            if recommended_qty > 0:
                priority = determine_priority(days_until_out)
                estimated_cost = recommended_qty * item.price
                
                recommendations.append({
                    "id": item.id,
                    "name": item.name,
                    "current_stock": item.quantity,
                    "min_stock": item.min_quantity,
                    "avg_daily": avg_daily,
                    "recommended_qty": recommended_qty,
                    "unit": item.unit,
                    "priority": priority,
                    "estimated_cost": estimated_cost,
                    "days_until_out_of_stock": days_until_out
                })
    
    # 우선순위에 따라 정렬 (긴급 > 보통 > 낮음)
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"].value, 3))
    
    return recommendations


def create_order(db: Session, order_data: OrderCreate):
    """발주 생성"""
    order = Order(status="pending")
    db.add(order)
    db.flush()
    
    total_cost = 0
    order_items_data = []
    
    for item_data in order_data.items:
        inventory_item = db.query(InventoryItem).filter(
            InventoryItem.id == item_data.inventory_item_id
        ).first()
        
        if not inventory_item:
            continue
        
        unit_price = inventory_item.price
        total_price = item_data.quantity * unit_price
        total_cost += total_price
        
        order_item = OrderItem(
            order_id=order.id,
            inventory_item_id=inventory_item.id,
            quantity=item_data.quantity,
            unit_price=unit_price,
            total_price=total_price,
            priority=item_data.priority
        )
        db.add(order_item)
        order_items_data.append({
            "id": order_item.id,
            "name": inventory_item.name,
            "quantity": order_item.quantity,
            "unit": inventory_item.unit,
            "unit_price": order_item.unit_price,
            "total_price": order_item.total_price,
            "priority": order_item.priority
        })
    
    order.total_cost = total_cost
    db.commit()
    db.refresh(order)
    
    return {
        "id": order.id,
        "status": order.status,
        "total_cost": order.total_cost,
        "items": order_items_data,
        "created_at": order.created_at,
        "updated_at": order.updated_at
    }

