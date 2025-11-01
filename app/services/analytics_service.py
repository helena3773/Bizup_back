from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.inventory import InventoryItem
from app.schemas.store import OutOfStockItemResponse
from typing import List


def get_out_of_stock_items(db: Session) -> List[OutOfStockItemResponse]:
    """품절 상품 조회 (품절 기간 및 예상 손실 포함)"""
    out_of_stock_items = db.query(InventoryItem).filter(
        InventoryItem.quantity == 0
    ).all()
    
    result = []
    today = datetime.now().date()
    
    for item in out_of_stock_items:
        # 품절 기간 계산 (last_updated 기준)
        days_out_of_stock = (today - item.last_updated).days
        
        # 상태 결정
        if days_out_of_stock >= 5:
            status = "critical"
        elif days_out_of_stock >= 2:
            status = "warning"
        else:
            status = "recent"
        
        # 예상 손실 계산 (일평균 판매 대비)
        # 간단한 추정: 단가 * 일평균 판매량 * 품절 기간
        avg_daily_usage = max(0.5, item.min_quantity / 30.0)
        estimated_loss = item.price * avg_daily_usage * days_out_of_stock
        
        result.append({
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "days_out_of_stock": days_out_of_stock,
            "last_stock": item.min_quantity,  # 마지막 재고량 (실제로는 이전 재고 기록 필요)
            "unit": item.unit,
            "estimated_loss": estimated_loss,
            "status": status
        })
    
    # 품절 기간이 긴 순으로 정렬
    result.sort(key=lambda x: x["days_out_of_stock"], reverse=True)
    
    return result


def get_inventory_stats(db: Session):
    """재고 통계 조회"""
    all_items = db.query(InventoryItem).all()
    
    total_items = len(all_items)
    low_stock_count = sum(1 for item in all_items if item.quantity <= item.min_quantity and item.quantity > 0)
    out_of_stock_count = sum(1 for item in all_items if item.quantity == 0)
    
    return {
        "total_items": total_items,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count
    }

