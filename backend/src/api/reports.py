from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, date, timedelta
from typing import Optional

from ..database import get_db
from ..models import Order, OrderItem, Dish, Category

router = APIRouter()

@router.get("/daily")
async def get_daily_report(
    report_date: Optional[date] = Query(None, description="Дата отчета (формат: YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Получить отчет за день"""
    if not report_date:
        report_date = date.today()
    
    # Получаем заказы за указанную дату
    orders = db.query(Order).filter(
        func.date(Order.order_date) == report_date
    ).all()
    
    # Сумма за день
    daily_total = sum(order.total_amount for order in orders)
    
    # Детали по заказам
    order_details = []
    for order in orders:
        items = db.query(OrderItem).filter(OrderItem.order_id == order.order_id).all()
        order_details.append({
            "order_id": order.order_id,
            "time": order.order_date.time().isoformat()[:5],
            "total": float(order.total_amount),
            "item_count": len(items)
        })
    
    return {
        "date": report_date.isoformat(),
        "orders_count": len(orders),
        "daily_total": float(daily_total),
        "average_order": float(daily_total / len(orders)) if orders else 0,
        "orders": order_details
    }

@router.get("/by-category")
async def get_category_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Отчет по категориям"""
    if not start_date:
        start_date = date.today() - timedelta(days=7)
    if not end_date:
        end_date = date.today()
    
    # Получаем продажи по категориям
    sales_by_category = db.query(
        Category.name,
        func.sum(OrderItem.quantity).label("total_quantity"),
        func.sum(OrderItem.item_total).label("total_amount")
    ).join(Dish, Dish.category_id == Category.category_id)\
     .join(OrderItem, OrderItem.dish_id == Dish.dish_id)\
     .join(Order, Order.order_id == OrderItem.order_id)\
     .filter(func.date(Order.order_date).between(start_date, end_date))\
     .group_by(Category.name)\
     .all()
    
    result = []
    total_amount = 0
    
    for category_name, quantity, amount in sales_by_category:
        result.append({
            "category": category_name,
            "quantity": quantity,
            "amount": float(amount)
        })
        total_amount += amount
    
    # Добавляем проценты
    for item in result:
        if total_amount > 0:
            item["percentage"] = round((item["amount"] / float(total_amount)) * 100, 1)
        else:
            item["percentage"] = 0
    
    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "total_amount": float(total_amount),
        "categories": result
    }

@router.get("/popular-dishes")
async def get_popular_dishes(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Самые популярные блюда"""
    popular = db.query(
        Dish.name,
        Category.name.label("category"),
        func.sum(OrderItem.quantity).label("total_sold"),
        func.sum(OrderItem.item_total).label("total_revenue")
    ).join(OrderItem, OrderItem.dish_id == Dish.dish_id)\
     .join(Category, Category.category_id == Dish.category_id)\
     .group_by(Dish.dish_id, Dish.name, Category.name)\
     .order_by(func.sum(OrderItem.quantity).desc())\
     .limit(limit)\
     .all()
    
    return [
        {
            "dish": dish_name,
            "category": category,
            "sold": total_sold,
            "revenue": float(total_revenue)
        }
        for dish_name, category, total_sold, total_revenue in popular
    ]
