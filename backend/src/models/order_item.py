from sqlalchemy import Column, Integer, Numeric, ForeignKey, String
from sqlalchemy.orm import relationship
import uuid
from ..database import Base

class OrderItem(Base):
    __tablename__ = "order_items"
    
    order_item_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String(36), ForeignKey("orders.order_id", ondelete="CASCADE"))
    dish_id = Column(String(36), ForeignKey("dishes.dish_id"))
    quantity = Column(Integer, nullable=False)
    item_total = Column(Numeric(10, 2), nullable=False)
    
    order = relationship("Order", backref="items")
    dish = relationship("Dish")
