from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.menu import MenuResponse
from app.services import menu_service

router = APIRouter(prefix="/menus", tags=["메뉴 관리"])


@router.post("/upload-csv")
async def upload_menu_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """CSV 파일 업로드하여 메뉴 등록 및 재료를 재고에 자동 등록"""
    print(f"\n{'='*60}")
    print(f"📤 CSV 업로드 요청 수신: {file.filename}")
    print(f"{'='*60}\n")
    
    try:
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        menus, inventory_items = menu_service.create_menu_from_csv(db, csv_content)
        
        # 등록된 재료 이름 목록
        ingredient_names = [item.name for item in inventory_items] if inventory_items else []
        
        # 실제로 재고에 등록된 항목 수 확인
        from app.models.inventory import InventoryItem
        total_inventory_count = db.query(InventoryItem).count()
        
        # 재료 카테고리로 필터링한 재고 개수 ("미정" 카테고리)
        ingredient_inventory_count = db.query(InventoryItem).filter(
            InventoryItem.category == "미정"
        ).count()
        
        message = f"{len(menus)}개 메뉴가 등록되었습니다"
        if inventory_items:
            message += f", {len(inventory_items)}개 재료가 재고에 자동 등록되었습니다"
        else:
            message += f" (재고에 이미 등록된 재료들이 있습니다)"
        
        print(f"\n{'='*60}")
        print(f"✅ CSV 업로드 완료")
        print(f"   - 메뉴: {len(menus)}개")
        print(f"   - 재료: {len(inventory_items)}개")
        print(f"   - 전체 재고 항목: {total_inventory_count}개")
        print(f"   - '미정' 카테고리 재고: {ingredient_inventory_count}개")
        print(f"{'='*60}\n")
        
        return {
            "message": message,
            "menus_count": len(menus),
            "ingredients_registered": len(inventory_items),
            "ingredient_names": ingredient_names,
            "total_inventory_count": total_inventory_count,
            "ingredient_inventory_count": ingredient_inventory_count,
            "menus": menus
        }
    except Exception as e:
        print(f"\n❌ CSV 업로드 오류: {e}")
        import traceback
        traceback.print_exc()
        raise


@router.get("/", response_model=List[MenuResponse])
def get_menus(db: Session = Depends(get_db)):
    """모든 메뉴 조회"""
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

