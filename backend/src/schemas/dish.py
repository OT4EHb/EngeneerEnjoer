from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class DishBase(BaseModel):
    name: str
    price: Decimal
    category_id: str

class DishCreate(DishBase):
    pass

class DishUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    category_id: Optional[str] = None

class Dish(DishBase):
    dish_id: str
    
    class Config:
        from_attributes = True
