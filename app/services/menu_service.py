from typing import List, Dict, Set, Tuple
from sqlalchemy.orm import Session
from app.models.menu import Menu, MenuIngredient
from app.models.inventory import InventoryItem
from app.schemas.menu import MenuCreate, MenuIngredientCreate
from app.schemas.inventory import InventoryItemCreate
from app.services import inventory_service


def parse_menu_csv(csv_content: str) -> List[MenuCreate]:
    menus = []
    lines = csv_content.strip().split('\n')
    print(f"CSV 라인 수: {len(lines)}")
    
    for line_idx, line in enumerate(lines, 1):
        if not line.strip():
            continue
            
        parts = [p.strip() for p in line.split(',')]
        if len(parts) < 2:
            print(f"라인 {line_idx}: 재료가 없음 (파트 수: {len(parts)})")
            continue
            
        menu_name = parts[0].strip()
        ingredients = []
        
        for ingredient_str in parts[1:]:
            ingredient_str = ingredient_str.strip()
            if not ingredient_str:
                continue
                
            if '-' in ingredient_str:
                name_part, qty_part = ingredient_str.rsplit('-', 1)
                try:
                    quantity = float(qty_part)
                    ingredient_name = name_part.strip()
                    
                    if ingredient_name:
                        ingredients.append(MenuIngredientCreate(
                            ingredient_name=ingredient_name,
                            quantity=quantity,
                            unit="ml"
                        ))
                        print(f"  ✓ 재료 파싱 성공: {ingredient_name}-{quantity}")
                    else:
                        print(f"재료명이 비어있음: '{ingredient_str}'")
                except ValueError as e:
                    print(f"수량 파싱 실패: '{ingredient_str}' - {e}")
                    continue
            else:
                print(f"재료 형식 오류 (하이픈 없음): '{ingredient_str}'")
        
        if ingredients:
            menus.append(MenuCreate(name=menu_name, ingredients=ingredients))
            print(f"메뉴 추가: {menu_name} ({len(ingredients)}개 재료)")
        else:
            print(f"라인 {line_idx}: 재료가 없어서 메뉴 추가 안 됨: {menu_name}")
    
    return menus


def create_menu_from_csv(db: Session, csv_content: str, mode: str = "add") -> Tuple[List[Menu], List[InventoryItem], Dict[str, int]]:
    mode = (mode or "add").lower()
    if mode not in {"add", "reset"}:
        mode = "add"
    print(f"메뉴 업로드 모드: {mode}")
    print(f"CSV 내용 파싱 시작...")
    print(f"CSV 내용 (처음 500자): {csv_content[:500]}")
    
    menus = parse_menu_csv(csv_content)
    print(f"파싱된 메뉴 수: {len(menus)}")
    for menu in menus:
        print(f"  - {menu.name}: {len(menu.ingredients)}개 재료")
        for ing in menu.ingredients:
            print(f"    * {ing.ingredient_name} ({ing.quantity})")
    
    all_ingredients: Set[str] = set()
    for menu_data in menus:
        for ing_data in menu_data.ingredients:
            all_ingredients.add(ing_data.ingredient_name)
    
    print(f"수집된 고유 재료 수: {len(all_ingredients)}")
    print(f"재료 목록: {list(all_ingredients)}")
    
    if len(all_ingredients) == 0:
        print("경고: 수집된 재료가 없습니다! CSV 형식을 확인하세요.")
        print("   예상 형식: 메뉴명,재료1-수량1,재료2-수량2,...")
    
    if mode == "reset":
        print("'초기화' 모드: 기존 메뉴, 재료, 재고를 모두 삭제합니다.")
        db.query(MenuIngredient).delete()
        db.query(Menu).delete()
        db.query(InventoryItem).delete()
        db.commit()
        print("기존 메뉴/재료/재고 삭제 완료.")
    
    created_inventory_items = []
    skipped_items = []
    new_items_count = 0
    print(f"총 {len(all_ingredients)}개 재료를 재고에 등록 시도...")
    
    for ingredient_name in all_ingredients:
        if not ingredient_name or not ingredient_name.strip():
            continue
            
        ingredient_name = ingredient_name.strip()
        
        existing_item = db.query(InventoryItem).filter(
            InventoryItem.name == ingredient_name
        ).first()
        
        if not existing_item:
            inventory_data = InventoryItemCreate(
                name=ingredient_name,
                category="-",
                quantity=0,
                unit="-",
                min_quantity=0,
                price=0
            )
            try:
                print(f"재고 생성 시도: {ingredient_name}...")
                new_item = inventory_service.create_inventory_item(db, inventory_data)
                created_inventory_items.append(new_item)
                new_items_count += 1
                print(f"재고 등록 성공: {ingredient_name} (ID: {new_item.id}, 초기화 상태)")
            except Exception as e:
                print(f"재고 등록 실패 ({ingredient_name}): {e}")
                import traceback
                traceback.print_exc()
        else:
            skipped_items.append(ingredient_name)
            print(f"재고에 이미 존재: {ingredient_name} (ID: {existing_item.id})")
            created_inventory_items.append(existing_item)
    
    print(f"재고 등록 완료: 총 {len(created_inventory_items)}개 항목 처리됨")
    print(f"   - 신규 등록: {new_items_count}개")
    print(f"   - 기존 항목: {len(skipped_items)}개")
    
    actual_count = db.query(InventoryItem).count()
    print(f"실제 DB의 재고 항목 수: {actual_count}개")
    
    if new_items_count == 0 and len(all_ingredients) > 0:
        print(f"경고: {len(all_ingredients)}개 재료가 수집되었지만 신규 등록된 항목이 없습니다.")
        print(f"   모든 재료가 이미 재고에 존재하거나 등록에 실패했을 수 있습니다.")
    
    created_menus = []
    menus_created = 0
    menus_updated = 0
    for menu_data in menus:
        existing_menu = None
        if mode == "add":
            existing_menu = db.query(Menu).filter(Menu.name == menu_data.name).first()
        
        if existing_menu:
            menus_updated += 1
            print(f"기존 메뉴 업데이트: {menu_data.name}")
            existing_ingredients = {
                ing.ingredient_name: ing for ing in existing_menu.ingredients
            }
            for ing_data in menu_data.ingredients:
                current = existing_ingredients.get(ing_data.ingredient_name)
                if current:
                    current.quantity = ing_data.quantity
                    current.unit = ing_data.unit
                    print(f"재료 업데이트: {ing_data.ingredient_name} -> {ing_data.quantity}{ing_data.unit}")
                else:
                    db_ingredient = MenuIngredient(
                        menu_id=existing_menu.id,
                        ingredient_name=ing_data.ingredient_name,
                        quantity=ing_data.quantity,
                        unit=ing_data.unit
                    )
                    db.add(db_ingredient)
                    print(f"재료 추가: {ing_data.ingredient_name} ({ing_data.quantity}{ing_data.unit})")
            created_menus.append(existing_menu)
        else:
            menus_created += 1
            db_menu = Menu(name=menu_data.name)
            db.add(db_menu)
            db.flush()
            
            for ing_data in menu_data.ingredients:
                db_ingredient = MenuIngredient(
                    menu_id=db_menu.id,
                    ingredient_name=ing_data.ingredient_name,
                    quantity=ing_data.quantity,
                    unit=ing_data.unit
                )
                db.add(db_ingredient)
            
            created_menus.append(db_menu)
    
    print(f"메뉴 처리 결과 - 새로 생성: {menus_created}개, 업데이트: {menus_updated}개")
    
    db.commit()
    stats = {
        "mode": mode,
        "menus_created": menus_created,
        "menus_updated": menus_updated if mode == "add" else 0,
        "inventory_registered": new_items_count
    }
    return created_menus, created_inventory_items, stats


def get_menu_ingredients(db: Session, menu_name: str) -> List[Dict]:
    menu = db.query(Menu).filter(Menu.name == menu_name).first()
    if not menu:
        return []
    
    return [
        {
            "ingredient_name": ing.ingredient_name,
            "quantity": ing.quantity,
            "unit": ing.unit
        }
        for ing in menu.ingredients
    ]


def get_all_menus(db: Session):
    return db.query(Menu).all()

