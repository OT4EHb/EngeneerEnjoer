from sqlalchemy import Column, DateTime, Numeric, func, String, text
import uuid
from ..database import Base
from datetime import *

class Order(Base):
    __tablename__ = "orders"
    
    order_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.order_date:
            # Устанавливаем московское время
            self.order_date = datetime.utcnow() + timedelta(hours=3)
    
    order_date = Column(DateTime)

    total_amount = Column(Numeric(10, 2), default=0.00)
