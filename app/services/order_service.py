from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.inventory import InventoryItem
from app.models.order import Order, OrderItem, OrderPriority
from app.schemas.order import OrderCreate
from typing import List, Dict



def calculate_days_until_out_of_stock(current_stock: float, avg_daily: float) -> int:
    if avg_daily <= 0:
        return 999
    return int(current_stock / avg_daily)


def calculate_recommended_quantity(
    current_stock: float,
    min_stock: float,
    avg_daily: float,
    days_buffer: int = 7
) -> float:
    needed_stock = min_stock + (avg_daily * days_buffer)
    recommended = needed_stock - current_stock
    return max(0, recommended)


def determine_priority(days_until_out: int) -> OrderPriority:
    if days_until_out <= 2:
        return OrderPriority.HIGH
    elif days_until_out <= 5:
        return OrderPriority.MEDIUM
    else:
        return OrderPriority.LOW

    inventory_items = db.query(InventoryItem).all()
    recommendations = []
    
    for item in inventory_items:
        avg_daily = calculate_avg_daily_usage(item)
        days_until_out = calculate_days_until_out_of_stock(item.quantity, avg_daily)
        
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
    
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"].value, 3))
    
    return recommendations


def create_order(db: Session, order_data: OrderCreate):
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

