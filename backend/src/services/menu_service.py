# src/services/menu_service.py
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid
from models import categories as category_models, dishes as dish_models
from schemas.menu import CategoryCreate, CategoryUpdate, DishCreate, DishUpdate

class MenuService:
    """Сервис для управления меню"""
    
    # Category methods
    @staticmethod
    def get_category(db: Session, category_id: str):
        return db.query(category_models.Category).filter(
            category_models.Category.id == category_id  # Исправлено
        ).first()
    
    @staticmethod
    def get_categories(db: Session, skip: int = 0, limit: int = 100):
        return db.query(category_models.Category).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_category(db: Session, category: CategoryCreate):
        category_id = str(uuid.uuid4())
        db_category = category_models.Category(id=category_id, **category.model_dump())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    
    @staticmethod
    def update_category(db: Session, category_id: str, category: CategoryUpdate):
        db_category = MenuService.get_category(db, category_id)
        if db_category:
            for key, value in category.model_dump(exclude_unset=True).items():
                setattr(db_category, key, value)
            db.commit()
            db.refresh(db_category)
        return db_category
    
    @staticmethod
    def delete_category(db: Session, category_id: str):
        db_category = MenuService.get_category(db, category_id)
        if db_category:
            db.delete(db_category)
            db.commit()
        return db_category
    
    # Dish methods
    @staticmethod
    def get_dish(db: Session, dish_id: str):
        return db.query(dish_models.Dish).filter(
            dish_models.Dish.id == dish_id  # Исправлено
        ).first()
    
    @staticmethod
    def get_dishes(db: Session, skip: int = 0, limit: int = 100, 
                   category_id: Optional[str] = None, available_only: bool = False):
        query = db.query(dish_models.Dish)
        
        if category_id:
            query = query.filter(dish_models.Dish.category_id == category_id)
        
        if available_only:
            query = query.filter(dish_models.Dish.is_available == True)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_dish(db: Session, dish: DishCreate):
        dish_id = str(uuid.uuid4())
        db_dish = dish_models.Dish(id=dish_id, **dish.model_dump())
        db.add(db_dish)
        db.commit()
        db.refresh(db_dish)
        return db_dish
    
    @staticmethod
    def update_dish(db: Session, dish_id: str, dish: DishUpdate):
        db_dish = MenuService.get_dish(db, dish_id)
        if db_dish:
            for key, value in dish.model_dump(exclude_unset=True).items():
                setattr(db_dish, key, value)
            db.commit()
            db.refresh(db_dish)
        return db_dish
    
    @staticmethod
    def delete_dish(db: Session, dish_id: str):
        db_dish = MenuService.get_dish(db, dish_id)
        if db_dish:
            db.delete(db_dish)
            db.commit()
        return db_dish
    
    @staticmethod
    def get_full_menu(db: Session):
        """Получить полное меню с категориями и блюдами"""
        categories = db.query(category_models.Category).all()
        dishes = db.query(dish_models.Dish).filter(
            dish_models.Dish.is_available == True
        ).all()
        
        # Добавляем категории к блюдам
        dishes_with_categories = []
        for dish in dishes:
            dish_dict = {c.name: getattr(dish, c.name) for c in dish.__table__.columns}
            dish_dict['category'] = dish.category
            dishes_with_categories.append(dish_dict)
        
        return {
            "categories": categories,
            "dishes": dishes_with_categories
        }
