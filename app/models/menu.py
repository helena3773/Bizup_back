from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Menu(Base):
    __tablename__ = "menus"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    
    ingredients = relationship("MenuIngredient", back_populates="menu", cascade="all, delete-orphan")


class MenuIngredient(Base):
    __tablename__ = "menu_ingredients"
    
    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=False)
    ingredient_name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False, default="ml")
    
    menu = relationship("Menu", back_populates="ingredients")

