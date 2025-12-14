from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..database import Base

class Category(Base):
    __tablename__ = "categories"
    
    # Для SQLite используем String вместо UUID
    category_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), nullable=False)
