from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import date
from app.database import get_db
from app.services import menu_service, inventory_service
from app.models.inventory import InventoryItem

router = APIRouter(prefix="/sales", tags=["매출 관리"])


class SaleItem(BaseModel):
    menu_name: str
    quantity: int
    timestamp: str


class SalesReceiveRequest(BaseModel):
    sales: List[SaleItem]


@router.post("/receive")
def receive_sales(sales_data: SalesReceiveRequest, db: Session = Depends(get_db)):
    """매출 데이터를 받아서 재고 차감"""
    results = []
    
    for sale in sales_data.sales:
        try:
            # 메뉴의 재료 리스트 가져오기
            ingredients = menu_service.get_menu_ingredients(db, sale.menu_name)
            
            if not ingredients:
                results.append({
                    "menu_name": sale.menu_name,
                    "status": "error",
                    "message": f"메뉴 '{sale.menu_name}'를 찾을 수 없습니다"
                })
                continue
            
            # 각 재료 차감
            deducted_items = []
            for ing in ingredients:
                ingredient_name = ing["ingredient_name"].strip()
                
                # 재고에서 재료 찾기 (정확한 이름 매칭)
                inventory_item = db.query(InventoryItem).filter(
                    InventoryItem.name == ingredient_name
                ).first()
                
                if inventory_item:
                    # 재고 차감 (수량 * 판매량)
                    old_quantity = inventory_item.quantity
                    total_deduct = ing["quantity"] * sale.quantity
                    new_quantity = max(0, inventory_item.quantity - total_deduct)
                    
                    inventory_item.quantity = new_quantity
                    inventory_item.last_updated = date.today()
                    
                    # 재고 상태 확인
                    status = inventory_service.get_stock_status(new_quantity, inventory_item.min_quantity)
                    old_status = inventory_service.get_stock_status(old_quantity, inventory_item.min_quantity)
                    
                    # 상태 변화 감지
                    status_changed = status != old_status
                    warning = None
                    if status_changed:
                        if status == "품절":
                            warning = f"⚠️ {inventory_item.name} 재고가 품절되었습니다!"
                        elif status == "부족":
                            warning = f"⚠️ {inventory_item.name} 재고가 부족합니다! (현재: {new_quantity}{inventory_item.unit}, 최소: {inventory_item.min_quantity}{inventory_item.unit})"
                    
                    deducted_items.append({
                        "ingredient": ing["ingredient_name"],
                        "deducted": total_deduct,
                        "remaining": new_quantity,
                        "old_quantity": old_quantity,
                        "status": status,
                        "status_changed": status_changed,
                        "warning": warning
                    })
                else:
                    # 재고에 없는 경우 - 경고 메시지
                    deducted_items.append({
                        "ingredient": ingredient_name,
                        "deducted": 0,
                        "remaining": 0,
                        "message": f"재고에 '{ingredient_name}'이(가) 등록되지 않았습니다. CSV 파일을 다시 업로드하세요."
                    })
                    print(f"⚠️ 경고: 재고에 '{ingredient_name}'이(가) 없습니다. 메뉴: {sale.menu_name}")
            
            db.commit()
            
            results.append({
                "menu_name": sale.menu_name,
                "quantity": sale.quantity,
                "status": "success",
                "deducted_items": deducted_items
            })
            
        except Exception as e:
            results.append({
                "menu_name": sale.menu_name,
                "status": "error",
                "message": str(e)
            })
    
    return {"results": results}

