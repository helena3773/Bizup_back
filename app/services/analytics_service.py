from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.inventory import InventoryItem
from app.schemas.store import OutOfStockItemResponse
from typing import List


def get_out_of_stock_items(db: Session) -> List[OutOfStockItemResponse]:
    out_of_stock_items = db.query(InventoryItem).filter(
        InventoryItem.quantity == 0
    ).all()
    
    result = []
    today = datetime.now().date()
    
    for item in out_of_stock_items:
        days_out_of_stock = (today - item.last_updated).days
        
        if days_out_of_stock >= 5:
            status = "critical"
        elif days_out_of_stock >= 2:
            status = "warning"
        else:
            status = "recent"
        
        avg_daily_usage = max(0.5, item.min_quantity / 30.0)
        estimated_loss = item.price * avg_daily_usage * days_out_of_stock
        
        result.append({
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "days_out_of_stock": days_out_of_stock,
            "last_stock": item.min_quantity,
            "unit": item.unit,
            "estimated_loss": estimated_loss,
            "status": status
        })
    
    result.sort(key=lambda x: x["days_out_of_stock"], reverse=True)
    
    return result


def get_inventory_stats(db: Session):
    all_items = db.query(InventoryItem).all()
    
    total_items = len(all_items)
    low_stock_count = sum(1 for item in all_items if item.quantity <= item.min_quantity and item.quantity > 0)
    out_of_stock_count = sum(1 for item in all_items if item.quantity == 0)
    
    return {
        "total_items": total_items,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count
    }

