# src/routers/cashier.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from database import get_db
from services.order_service import OrderService
from schemas.orders import OrderCreate

router = APIRouter(prefix="/cashier", tags=["cashier"])

@router.post("/quick-sale")
async def create_quick_sale(
    order: OrderCreate,
    db: Session = Depends(get_db)
):
    """
    Быстрая продажа для кассира.
    Просто фиксирует какие блюда и в каком количестве были проданы.
    """
    try:
        # Автоматически заполняем информацию для кассового чека
        order.customer_name = "Кассовый чек"
        order.customer_phone = None
        order.status = "completed"  # Сразу завершен
        
        created_order = OrderService.create_order(db, order)
        
        return {
            "success": True,
            "order_id": created_order.id,
            "receipt_number": f"ЧЕК-{created_order.id[:8].upper()}",
            "total_amount": created_order.total_amount,
            "created_at": created_order.order_date
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания чека: {str(e)}")

@router.get("/today-sales")
async def get_today_sales(
    db: Session = Depends(get_db)
):
    """Получить сегодняшние продажи для кассира"""
    from sqlalchemy import func
    
    today = datetime.now().date()
    
    # Получаем заказы за сегодня
    orders = OrderService.get_orders(
        db, 
        date_from=today,
        status="completed"
    )
    
    total_sales = len(orders)
    total_revenue = sum(order.total_amount for order in orders)
    
    # Группируем по часам
    hourly_sales = {}
    for order in orders:
        hour = order.order_date.hour
        hourly_sales[hour] = hourly_sales.get(hour, 0) + order.total_amount
    
    return {
        "date": today.isoformat(),
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "hourly_sales": hourly_sales,
        "orders": orders[:10]  # Последние 10 заказов
    }
