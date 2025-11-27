from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
    InventoryItemWithStatus
)
from app.services import inventory_service

router = APIRouter(prefix="/inventory", tags=["재고 관리"])


@router.get("/", response_model=List[InventoryItemWithStatus])
def get_inventory_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),  # 기본값을 1000으로 증가, 최대값도 증가
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    items = inventory_service.get_inventory_items(db, skip=skip, limit=limit, search=search)
    
    result = []
    for item in items:
        status = inventory_service.get_stock_status(item.quantity, item.min_quantity)
        item_dict = {
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "quantity": item.quantity,
            "unit": item.unit,
            "min_quantity": item.min_quantity,
            "price": item.price,
            "last_updated": item.last_updated,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
            "status": status
        }
        result.append(InventoryItemWithStatus(**item_dict))
    
    return result


@router.get("/stats")
def get_inventory_stats(db: Session = Depends(get_db)):
    from app.services import analytics_service
    
    stats = analytics_service.get_inventory_stats(db)
    return stats


@router.get("/low-stock", response_model=List[InventoryItemWithStatus])
def get_low_stock_items(db: Session = Depends(get_db)):
    items = inventory_service.get_low_stock_items(db)
    result = []
    for item in items:
        status = inventory_service.get_stock_status(item.quantity, item.min_quantity)
        item_dict = {
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "quantity": item.quantity,
            "unit": item.unit,
            "min_quantity": item.min_quantity,
            "price": item.price,
            "last_updated": item.last_updated,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
            "status": status
        }
        result.append(InventoryItemWithStatus(**item_dict))
    return result


@router.get("/{item_id}", response_model=InventoryItemResponse)
def get_inventory_item(item_id: int, db: Session = Depends(get_db)):
    item = inventory_service.get_inventory_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="재고 아이템을 찾을 수 없습니다")
    return item


@router.post("/", response_model=InventoryItemResponse, status_code=201)
def create_inventory_item(item: InventoryItemCreate, db: Session = Depends(get_db)):
    return inventory_service.create_inventory_item(db, item)


@router.put("/{item_id}", response_model=InventoryItemResponse)
def update_inventory_item(
    item_id: int,
    item: InventoryItemUpdate,
    db: Session = Depends(get_db)
):
    updated_item = inventory_service.update_inventory_item(db, item_id, item)
    if not updated_item:
        raise HTTPException(status_code=404, detail="재고 아이템을 찾을 수 없습니다")
    return updated_item


@router.delete("/{item_id}", status_code=204)
def delete_inventory_item(item_id: int, db: Session = Depends(get_db)):
    success = inventory_service.delete_inventory_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="재고 아이템을 찾을 수 없습니다")
    return None

