from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.inventory import InventoryItem
from app.schemas.inventory import InventoryItemCreate, InventoryItemUpdate
from datetime import date


def get_inventory_items(db: Session, skip: int = 0, limit: int = 100, search: str = None):
    """재고 목록 조회"""
    query = db.query(InventoryItem)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                InventoryItem.name.like(search_term),
                InventoryItem.category.like(search_term)
            )
        )
    
    return query.offset(skip).limit(limit).all()


def get_inventory_item(db: Session, item_id: int):
    """특정 재고 아이템 조회"""
    return db.query(InventoryItem).filter(InventoryItem.id == item_id).first()


def create_inventory_item(db: Session, item: InventoryItemCreate):
    """재고 아이템 생성"""
    db_item = InventoryItem(
        name=item.name,
        category=item.category,
        quantity=item.quantity,
        unit=item.unit,
        min_quantity=item.min_quantity,
        price=item.price,
        last_updated=date.today()
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_inventory_item(db: Session, item_id: int, item: InventoryItemUpdate):
    """재고 아이템 업데이트"""
    db_item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not db_item:
        return None
    
    update_data = item.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db_item.last_updated = date.today()
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_inventory_item(db: Session, item_id: int):
    """재고 아이템 삭제"""
    db_item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not db_item:
        return False
    db.delete(db_item)
    db.commit()
    return True


def get_stock_status(quantity: float, min_quantity: float) -> str:
    """재고 상태 계산"""
    if quantity == 0:
        return "품절"
    elif quantity <= min_quantity:
        return "부족"
    else:
        return "정상"


def get_low_stock_items(db: Session):
    """재고 부족 아이템 조회"""
    return db.query(InventoryItem).filter(
        InventoryItem.quantity <= InventoryItem.min_quantity,
        InventoryItem.quantity > 0
    ).all()


def get_out_of_stock_items(db: Session):
    """품절 아이템 조회"""
    return db.query(InventoryItem).filter(InventoryItem.quantity == 0).all()

