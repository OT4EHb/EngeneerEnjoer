from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..database import get_db
from ..models import *
from ..schemas.category import CategoryCreate, CategoryUpdate
from ..schemas.dish import DishCreate, DishUpdate

router = APIRouter()

# --- Категории ---
@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Получить все категории"""
    return db.query(Category).all()

@router.post("/categories")
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Создать новую категорию"""
    new_category = Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.put("/categories/{category_id}")
async def update_category(category_id: str, category: CategoryUpdate, db: Session = Depends(get_db)):
    """Обновить категорию"""
    db_category = db.query(Category).filter(Category.category_id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    
    db_category.name = category.name
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/categories/{category_id}")
async def delete_category(category_id: str, db: Session = Depends(get_db)):
    """Удалить категорию"""
    db_category = db.query(Category).filter(Category.category_id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    
    # Проверяем, есть ли блюда в категории
    dishes_count = db.query(Dish).filter(Dish.category_id == category_id).count()
    if dishes_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Невозможно удалить категорию, в ней {dishes_count} блюд"
        )
    
    db.delete(db_category)
    db.commit()
    return {"message": "Категория удалена"}

# --- Блюда ---
@router.get("/dishes")
async def get_dishes(db: Session = Depends(get_db)):
    """Получить все блюда"""
    dishes = db.query(Dish).join(Category).all()
    result = []
    for dish in dishes:
        result.append({
            "dish_id": dish.dish_id,
            "name": dish.name,
            "price": float(dish.price),
            "category_id": dish.category_id,
            "category_name": dish.category.name if dish.category else ""
        })
    return result

@router.post("/dishes")
async def create_dish(dish: DishCreate, db: Session = Depends(get_db)):
    """Создать новое блюдо"""
    # Проверяем существование категории
    category = db.query(Category).filter(Category.category_id == dish.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    
    new_dish = Dish(
        name=dish.name,
        price=dish.price,
        category_id=dish.category_id
    )
    
    db.add(new_dish)
    db.commit()
    db.refresh(new_dish)
    return new_dish

@router.put("/dishes/{dish_id}")
async def update_dish(dish_id: str, dish: DishUpdate, db: Session = Depends(get_db)):
    """Обновить блюдо"""
    db_dish = db.query(Dish).filter(Dish.dish_id == dish_id).first()
    if not db_dish:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")
    
    # Если обновляется категория, проверяем её существование
    if dish.category_id:
        category = db.query(Category).filter(Category.category_id == dish.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Категория не найдена")
        db_dish.category_id = dish.category_id
    
    if dish.name:
        db_dish.name = dish.name
    if dish.price:
        db_dish.price = dish.price
    
    db.commit()
    db.refresh(db_dish)
    return db_dish

@router.delete("/dishes/{dish_id}")
async def delete_dish(dish_id: str, db: Session = Depends(get_db)):
    """Удалить блюдо"""
    db_dish = db.query(Dish).filter(Dish.dish_id == dish_id).first()
    if not db_dish:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")
    
    # Проверяем, есть ли это блюдо в заказах
    order_items_count = db.query(OrderItem).filter(OrderItem.dish_id == dish_id).count()
    if order_items_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Невозможно удалить блюдо, оно есть в {order_items_count} заказах"
        )
    
    db.delete(db_dish)
    db.commit()
    return {"message": "Блюдо удалено"}

@router.get("/orders/by-date")
async def get_orders_by_date(
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """Получить заказы по диапазону дат"""
    from datetime import datetime, date
    from sqlalchemy import func, and_

    # Если даты не указаны, возвращаем все заказы
    query = db.query(Order)

    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(func.date(Order.order_date) >= start)
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат начальной даты")

    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(func.date(Order.order_date) <= end)
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат конечной даты")

    # Получаем заказы
    orders = query.order_by(Order.order_date.desc()).all()

    result = []
    for order in orders:
        # Подсчитываем количество позиций
        item_count = db.query(OrderItem).filter(
            OrderItem.order_id == order.order_id
        ).count()

        # Форматируем дату и время
        formatted_date = ""
        formatted_time = ""

        if order.order_date:
            formatted_date = order.order_date.strftime("%d.%m.%Y")
            formatted_time = order.order_date.strftime("%H:%M")

        result.append({
            "order_id": order.order_id,
            "date": formatted_date,
            "time": formatted_time,
            "order_date": order.order_date.isoformat() if order.order_date else None,
            "total": float(order.total_amount),
            "total_amount": float(order.total_amount),
            "item_count": item_count
        })

    return result
