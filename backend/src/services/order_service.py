# src/services/order_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime, date
from models import orders as order_models, order_items as order_item_models, dishes as dish_models
from schemas.orders import OrderCreate, OrderUpdate, OrderItemCreate

class OrderService:
    """Сервис для управления заказами"""
    
    @staticmethod
    def get_order(db: Session, order_id: str):
        return db.query(order_models.Order).filter(
            order_models.Order.id == order_id  # Исправлено
        ).first()
    
    @staticmethod
    def get_orders(db: Session, skip: int = 0, limit: int = 100, 
                   status: Optional[str] = None, date_from: Optional[date] = None):
        query = db.query(order_models.Order)
        
        if status:
            query = query.filter(order_models.Order.status == status)
        
        if date_from:
            query = query.filter(order_models.Order.order_date >= date_from)
        
        return query.order_by(order_models.Order.order_date.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_order(db: Session, order: OrderCreate):
        # Проверяем доступность блюд
        for item in order.items:
            dish = db.query(dish_models.Dish).filter(
                dish_models.Dish.id == item.dish_id,  # Исправлено
                dish_models.Dish.is_available == True
            ).first()
            
            if not dish:
                raise ValueError(f"Dish {item.dish_id} is not available")
        
        # Рассчитываем общую сумму
        total_amount = sum(item.item_total for item in order.items)
        
        # Создаем заказ
        order_id = str(uuid.uuid4())
        db_order = order_models.Order(
            id=order_id,
            total_amount=total_amount,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            status="pending"
        )
        db.add(db_order)
        
        # Создаем элементы заказа
        for item in order.items:
            item_id = str(uuid.uuid4())
            db_item = order_item_models.OrderItem(
                id=item_id,
                order_id=order_id,  # Исправлено
                dish_id=item.dish_id,
                quantity=item.quantity,
                item_total=item.item_total
            )
            db.add(db_item)
        
        db.commit()
        db.refresh(db_order)
        return db_order
    
    @staticmethod
    def update_order(db: Session, order_id: str, order: OrderUpdate):
        db_order = OrderService.get_order(db, order_id)
        if db_order:
            for key, value in order.dict(exclude_unset=True).items():
                setattr(db_order, key, value)
            db.commit()
            db.refresh(db_order)
        return db_order
    
    @staticmethod
    def delete_order(db: Session, order_id: str):
        db_order = OrderService.get_order(db, order_id)
        if db_order:
            db.delete(db_order)
            db.commit()
        return db_order
    
    @staticmethod
    def get_order_statistics(db: Session, start_date: date, end_date: date):
        """Получить статистику по заказам за период"""
        from sqlalchemy import func
        
        result = db.query(
            func.count(order_models.Order.id).label('total_orders'),  # Исправлено
            func.sum(order_models.Order.total_amount).label('total_revenue'),
            func.avg(order_models.Order.total_amount).label('avg_order_value')
        ).filter(
            order_models.Order.order_date >= start_date,
            order_models.Order.order_date <= end_date,
            order_models.Order.status == 'completed'
        ).first()
        
        return {
            'total_orders': result.total_orders or 0,
            'total_revenue': float(result.total_revenue or 0),
            'avg_order_value': float(result.avg_order_value or 0)
        }
