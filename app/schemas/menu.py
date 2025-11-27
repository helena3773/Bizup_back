from pydantic import BaseModel
from typing import List


class MenuIngredientCreate(BaseModel):
    ingredient_name: str
    quantity: float
    unit: str = "ml"


class MenuIngredientResponse(BaseModel):
    ingredient_name: str
    quantity: float
    unit: str
    
    class Config:
        from_attributes = True


class MenuCreate(BaseModel):
    name: str
    ingredients: List[MenuIngredientCreate]


class MenuResponse(BaseModel):
    id: int
    name: str
    ingredients: List[MenuIngredientResponse]
    
    class Config:
        from_attributes = True

