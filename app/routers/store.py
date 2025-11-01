from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.store import (
    StoreResponse,
    StoreUpdate,
    NotificationSettingsResponse,
    NotificationSettingsUpdate
)
from app.models.store import Store, NotificationSettings

router = APIRouter(prefix="/store", tags=["가게 설정"])


@router.get("/", response_model=StoreResponse)
def get_store(db: Session = Depends(get_db)):
    """가게 정보 조회"""
    store = db.query(Store).first()
    if not store:
        # 기본 가게 정보 생성
        store = Store(name="우리 카페", address="", phone="")
        db.add(store)
        db.commit()
        db.refresh(store)
    return store


@router.put("/", response_model=StoreResponse)
def update_store(store_data: StoreUpdate, db: Session = Depends(get_db)):
    """가게 정보 업데이트"""
    store = db.query(Store).first()
    if not store:
        store = Store(**store_data.dict(exclude_unset=True))
        db.add(store)
    else:
        update_data = store_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(store, field, value)
    
    db.commit()
    db.refresh(store)
    return store


@router.get("/notifications", response_model=NotificationSettingsResponse)
def get_notification_settings(db: Session = Depends(get_db)):
    """알림 설정 조회"""
    settings = db.query(NotificationSettings).first()
    if not settings:
        # 기본 알림 설정 생성
        settings = NotificationSettings(
            low_stock=True,
            out_of_stock=True,
            order_reminder=True,
            daily_report=False
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.put("/notifications", response_model=NotificationSettingsResponse)
def update_notification_settings(
    settings_data: NotificationSettingsUpdate,
    db: Session = Depends(get_db)
):
    """알림 설정 업데이트"""
    settings = db.query(NotificationSettings).first()
    if not settings:
        settings = NotificationSettings(**settings_data.dict())
        db.add(settings)
    else:
        update_data = settings_data.dict()
        for field, value in update_data.items():
            setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    return settings

