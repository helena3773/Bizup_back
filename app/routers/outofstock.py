from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.store import OutOfStockItemResponse, OutOfStockMenuResponse
from app.services import analytics_service, inventory_service
from pydantic import BaseModel

router = APIRouter(prefix="/out-of-stock", tags=["품절 관리"])


class OutOfStockResponse(BaseModel):
    items: List[OutOfStockItemResponse]
    menus: List[OutOfStockMenuResponse]


@router.get("/", response_model=OutOfStockResponse)
def get_out_of_stock_items(db: Session = Depends(get_db)):
    items = analytics_service.get_out_of_stock_items(db)
    menus = analytics_service.get_out_of_stock_menus(db)
    return {
        "items": items,
        "menus": menus
    }


@router.post("/{item_id}/restock")
def restock_item(
    item_id: int,
    quantity: float = Query(..., gt=0, description="재입고 수량"),
    db: Session = Depends(get_db)
):
    from app.schemas.inventory import InventoryItemUpdate
    
    item = inventory_service.get_inventory_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="재고 아이템을 찾을 수 없습니다")
    
    update_data = InventoryItemUpdate(quantity=quantity)
    updated_item = inventory_service.update_inventory_item(db, item_id, update_data)
    
    return {
        "message": "재입고가 완료되었습니다",
        "item": updated_item
    }

