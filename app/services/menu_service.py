from typing import List, Dict, Set
from sqlalchemy.orm import Session
from app.models.menu import Menu, MenuIngredient
from app.models.inventory import InventoryItem
from app.schemas.menu import MenuCreate, MenuIngredientCreate
from app.schemas.inventory import InventoryItemCreate
from app.services import inventory_service


def parse_menu_csv(csv_content: str) -> List[MenuCreate]:
    """CSV 내용을 파싱하여 메뉴 리스트 반환"""
    menus = []
    lines = csv_content.strip().split('\n')
    print(f"📝 CSV 라인 수: {len(lines)}")
    
    for line_idx, line in enumerate(lines, 1):
        if not line.strip():
            continue
            
        parts = [p.strip() for p in line.split(',')]
        if len(parts) < 2:
            print(f"⚠️ 라인 {line_idx}: 재료가 없음 (파트 수: {len(parts)})")
            continue
            
        menu_name = parts[0].strip()
        ingredients = []
        
        for ingredient_str in parts[1:]:
            ingredient_str = ingredient_str.strip()
            if not ingredient_str:
                continue
                
            # "재료명-수량" 형식 파싱
            if '-' in ingredient_str:
                name_part, qty_part = ingredient_str.rsplit('-', 1)
                try:
                    quantity = float(qty_part)
                    ingredient_name = name_part.strip()
                    
                    if ingredient_name:  # 재료명이 비어있지 않은 경우만
                        ingredients.append(MenuIngredientCreate(
                            ingredient_name=ingredient_name,
                            quantity=quantity,
                            unit="ml"  # 기본 단위, 필요시 파싱
                        ))
                        print(f"  ✓ 재료 파싱 성공: {ingredient_name}-{quantity}")
                    else:
                        print(f"  ⚠️ 재료명이 비어있음: '{ingredient_str}'")
                except ValueError as e:
                    print(f"  ⚠️ 수량 파싱 실패: '{ingredient_str}' - {e}")
                    continue
            else:
                print(f"  ⚠️ 재료 형식 오류 (하이픈 없음): '{ingredient_str}'")
        
        if ingredients:
            menus.append(MenuCreate(name=menu_name, ingredients=ingredients))
            print(f"✅ 메뉴 추가: {menu_name} ({len(ingredients)}개 재료)")
        else:
            print(f"⚠️ 라인 {line_idx}: 재료가 없어서 메뉴 추가 안 됨: {menu_name}")
    
    return menus


def create_menu_from_csv(db: Session, csv_content: str):
    """CSV 내용을 파싱하여 메뉴들을 DB에 저장하고, 재료들을 재고에 자동 등록"""
    print(f"📄 CSV 내용 파싱 시작...")
    print(f"📄 CSV 내용 (처음 500자): {csv_content[:500]}")
    
    menus = parse_menu_csv(csv_content)
    print(f"📋 파싱된 메뉴 수: {len(menus)}")
    for menu in menus:
        print(f"  - {menu.name}: {len(menu.ingredients)}개 재료")
        for ing in menu.ingredients:
            print(f"    * {ing.ingredient_name} ({ing.quantity}{ing.unit})")
    
    # 모든 재료 수집 (중복 제거)
    all_ingredients: Set[str] = set()
    for menu_data in menus:
        for ing_data in menu_data.ingredients:
            all_ingredients.add(ing_data.ingredient_name)
    
    print(f"📦 수집된 고유 재료 수: {len(all_ingredients)}")
    print(f"📦 재료 목록: {list(all_ingredients)}")
    
    if len(all_ingredients) == 0:
        print("❌ 경고: 수집된 재료가 없습니다! CSV 형식을 확인하세요.")
        print("   예상 형식: 메뉴명,재료1-수량1,재료2-수량2,...")
    
    # 재료들을 재고에 자동 등록
    created_inventory_items = []
    skipped_items = []
    new_items_count = 0
    print(f"📦 총 {len(all_ingredients)}개 재료를 재고에 등록 시도...")
    
    for ingredient_name in all_ingredients:
        if not ingredient_name or not ingredient_name.strip():
            continue
            
        ingredient_name = ingredient_name.strip()
        
        # 이미 재고에 있는지 확인 (정확한 이름 매칭)
        existing_item = db.query(InventoryItem).filter(
            InventoryItem.name == ingredient_name
        ).first()
        
        if not existing_item:
            # 재고에 없으면 새로 생성 (기본값 설정)
            inventory_data = InventoryItemCreate(
                name=ingredient_name,
                category="미정",  # 기본 카테고리
                quantity=100,  # 기본 수량
                unit="ml",  # 기본 단위
                min_quantity=5,  # 기본 최소 수량
                price=1200  # 기본 가격
            )
            try:
                print(f"  🔄 재고 생성 시도: {ingredient_name}...")
                new_item = inventory_service.create_inventory_item(db, inventory_data)
                created_inventory_items.append(new_item)
                new_items_count += 1
                print(f"✅ 재고 등록 성공: {ingredient_name} (ID: {new_item.id}, 수량: 100, 최소: 5, 가격: 1200)")
            except Exception as e:
                print(f"❌ 재고 등록 실패 ({ingredient_name}): {e}")
                import traceback
                traceback.print_exc()
                # 실패해도 계속 진행
        else:
            skipped_items.append(ingredient_name)
            # 이미 존재하는 경우에도 기본값이 없거나 0이면 업데이트
            updated = False
            if existing_item.quantity == 0:
                existing_item.quantity = 100
                updated = True
            if existing_item.min_quantity == 0:
                existing_item.min_quantity = 5
                updated = True
            if existing_item.price == 0:
                existing_item.price = 1200
                updated = True
            if not existing_item.category or existing_item.category == "":
                existing_item.category = "미정"
                updated = True
            
            if updated:
                from datetime import date
                existing_item.last_updated = date.today()
                db.commit()
                db.refresh(existing_item)
                print(f"🔄 재고 업데이트: {ingredient_name} (ID: {existing_item.id}, 수량: {existing_item.quantity}, 최소: {existing_item.min_quantity}, 가격: {existing_item.price})")
            else:
                print(f"⏭️  재고에 이미 존재: {ingredient_name} (ID: {existing_item.id})")
            
            created_inventory_items.append(existing_item)
    
    print(f"📊 재고 등록 완료: 총 {len(created_inventory_items)}개 항목 처리됨")
    print(f"   - 신규 등록: {new_items_count}개")
    print(f"   - 기존 항목: {len(skipped_items)}개")
    
    # 실제 DB에 등록된 재고 항목 수 확인
    actual_count = db.query(InventoryItem).count()
    print(f"📊 실제 DB의 재고 항목 수: {actual_count}개")
    
    if new_items_count == 0 and len(all_ingredients) > 0:
        print(f"⚠️ 경고: {len(all_ingredients)}개 재료가 수집되었지만 신규 등록된 항목이 없습니다.")
        print(f"   모든 재료가 이미 재고에 존재하거나 등록에 실패했을 수 있습니다.")
    
    # 메뉴들 저장
    created_menus = []
    for menu_data in menus:
        # 기존 메뉴 확인
        existing_menu = db.query(Menu).filter(Menu.name == menu_data.name).first()
        if existing_menu:
            # 기존 메뉴 삭제 후 재생성
            db.delete(existing_menu)
            db.commit()
        
        # 새 메뉴 생성
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
    
    db.commit()
    return created_menus, created_inventory_items


def get_menu_ingredients(db: Session, menu_name: str) -> List[Dict]:
    """메뉴 이름으로 재료 리스트 조회"""
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
    """모든 메뉴 조회"""
    return db.query(Menu).all()

