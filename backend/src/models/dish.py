from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from ..database import Base

class Dish(Base):
    __tablename__ = "dishes"
    
    dish_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id = Column(String(36), ForeignKey("categories.category_id"))
    name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    
    category = relationship("Category", backref="dishes")
