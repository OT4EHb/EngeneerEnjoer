from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class OrderItemCreate(BaseModel):
    dish_id: str
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderItemResponse(BaseModel):
    dish_name: str
    quantity: int
    price_per_item: Decimal
    item_total: Decimal

class OrderResponse(BaseModel):
    order_id: str
    order_date: datetime
    total_amount: Decimal
    items: List[OrderItemResponse]
    
    class Config:
        from_attributes = True
