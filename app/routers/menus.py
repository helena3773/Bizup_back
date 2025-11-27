from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.menu import MenuResponse
from app.services import menu_service

router = APIRouter(prefix="/menus", tags=["메뉴 관리"])


@router.post("/upload-csv")
async def upload_menu_csv(
    file: UploadFile = File(...),
    mode: str = Query("add", pattern="^(add|reset)$"),
    db: Session = Depends(get_db)
):
    print(f"\n{'='*60}")
    print(f"CSV 업로드 요청 수신: {file.filename}")
    print(f"{'='*60}\n")
    
    try:
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        menus, inventory_items, stats = menu_service.create_menu_from_csv(db, csv_content, mode)
        
        ingredient_names = [item.name for item in inventory_items] if inventory_items else []
        
        from app.models.inventory import InventoryItem
        total_inventory_count = db.query(InventoryItem).count()
        
        ingredient_inventory_count = db.query(InventoryItem).filter(
            InventoryItem.category == "미정"
        ).count()
        
        action_label = "추가" if mode == "add" else "초기화"
        message = f"[{action_label}] {len(menus)}개 메뉴 데이터를 처리했습니다."
        if mode == "add":
            message += f" (신규 {stats['menus_created']}개, 업데이트 {stats['menus_updated']}개)"
        else:
            message += f" (전체 {stats['menus_created']}개 메뉴 재구성)"
        
        print(f"\n{'='*60}")
        print(f"CSV 업로드 완료")
        print(f"   - 메뉴: {len(menus)}개")
        print(f"   - 재료: {len(inventory_items)}개")
        print(f"   - 전체 재고 항목: {total_inventory_count}개")
        print(f"   - '미정' 카테고리 재고: {ingredient_inventory_count}개")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "mode": mode,
            "message": message,
            "menus_count": len(menus),
            "menus_created": stats["menus_created"],
            "menus_updated": stats["menus_updated"],
            "ingredients_registered": stats["inventory_registered"],
            "ingredient_names": ingredient_names,
            "total_inventory_count": total_inventory_count,
            "ingredient_inventory_count": ingredient_inventory_count,
            "menus": menus
        }
    except Exception as e:
        print(f"\nCSV 업로드 오류: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "mode": mode,
            "message": str(e)
        }


@router.get("/", response_model=List[MenuResponse])
def get_menus(db: Session = Depends(get_db)):
    menus = menu_service.get_all_menus(db)
    result = []
    for menu in menus:
        result.append(MenuResponse(
            id=menu.id,
            name=menu.name,
            ingredients=[
                {
                    "ingredient_name": ing.ingredient_name,
                    "quantity": ing.quantity,
                    "unit": ing.unit
                }
                for ing in menu.ingredients
            ]
        ))
    return result

