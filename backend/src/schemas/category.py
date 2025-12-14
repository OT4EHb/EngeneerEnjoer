from pydantic import BaseModel

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class Category(CategoryBase):
    category_id: str
    
    class Config:
        from_attributes = True  # Заменяет orm_mode = True в Pydantic v2
