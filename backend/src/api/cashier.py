from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import uuid

from ..database import get_db
from ..models import Dish, Category, Order, OrderItem
from ..schemas.order import OrderCreate, OrderResponse

router = APIRouter()

@router.get("/menu")
async def get_menu(db: Session = Depends(get_db)):
    """Получить все блюда с категориями"""
    try:
        dishes = db.query(Dish).join(Category).all()
        
        menu = []
        for dish in dishes:
            menu.append({
                "dish_id": dish.dish_id,
                "name": dish.name,
                "price": float(dish.price),
                "category_id": dish.category_id,
                "category_name": dish.category.name if dish.category else "Без категории"
            })
        
        # Группируем по категориям
        categories = {}
        for item in menu:
            cat_name = item["category_name"]
            if cat_name not in categories:
                categories[cat_name] = []
            categories[cat_name].append(item)
        
        return categories
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения меню: {str(e)}")

@router.post("/order", response_model=dict)
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """Создать новый заказ"""
    try:
        # Создаем запись заказа
        new_order = Order()
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        
        total_amount = 0
        
        # Добавляем каждое блюдо в заказ
        for item in order_data.items:
            # Проверяем существование блюда
            dish = db.query(Dish).filter(Dish.dish_id == item.dish_id).first()
            if not dish:
                db.rollback()
                raise HTTPException(status_code=404, detail=f"Блюдо не найдено: {item.dish_id}")
            
            # Рассчитываем стоимость позиции
            item_total = dish.price * item.quantity
            
            # Создаем позицию заказа
            order_item = OrderItem(
                order_id=new_order.order_id,
                dish_id=item.dish_id,
                quantity=item.quantity,
                item_total=item_total
            )
            
            db.add(order_item)
            total_amount += item_total
        
        # Обновляем общую сумму заказа
        new_order.total_amount = total_amount
        db.commit()
        
        return {
            "success": True,
            "order_id": new_order.order_id,
            "total_amount": float(total_amount),
            "message": "Заказ успешно создан"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка создания заказа: {str(e)}")

@router.get("/orders/today")
async def get_today_orders(db: Session = Depends(get_db)):
    """Получить сегодняшние заказы"""
    from datetime import datetime, date
    
    today = date.today()
    
    orders = db.query(Order).filter(
        func.date(Order.order_date) == today
    ).order_by(Order.order_date.desc()).all()
    
    result = []
    for order in orders:
        # Подсчитываем количество позиций в заказе
        item_count = db.query(OrderItem).filter(
            OrderItem.order_id == order.order_id
        ).count()
        
        result.append({
            "order_id": order.order_id,
            "order_date": order.order_date.isoformat(),
            "total_amount": float(order.total_amount),
            "item_count": item_count
        })
    
    return result

@router.get("/orders/{order_id}")
async def get_order_details(order_id: str, db: Session = Depends(get_db)):
    """Получить детали конкретного заказа"""
    try:
        # Ищем заказ
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Заказ не найден")

        # Получаем все позиции заказа с информацией о блюдах
        order_items = db.query(OrderItem).join(Dish).filter(
            OrderItem.order_id == order_id
        ).all()

        items = []
        total_amount = 0

        for item in order_items:
            items.append({
                "dish_id": item.dish_id,
                "dish_name": item.dish.name if item.dish else "Неизвестное блюдо",
                "quantity": item.quantity,
                "price_per_item": float(item.dish.price) if item.dish else 0,
                "item_total": float(item.item_total)
            })
            total_amount += item.item_total

        return {
            "order_id": order.order_id,
            "order_date": order.order_date.isoformat(),
            "total_amount": float(total_amount),
            "items": items
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения заказа: {str(e)}")
