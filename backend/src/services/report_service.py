# src/services/report_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
from models import orders as order_models, order_items as order_item_models
from models import dishes as dish_models, categories as category_models
from schemas.reports import SalesReport, PopularDish, RevenueByCategory, DailyRevenue

class ReportService:
    """Сервис для генерации отчетов"""
    
    @staticmethod
    def get_sales_report(db: Session, start_date: date, end_date: date) -> SalesReport:
        """Отчет по продажам за период"""
        # Основная статистика - ИСПРАВЛЕНО: используем id вместо order_id
        stats = db.query(
            func.count(order_models.Order.id).label('total_orders'),
            func.sum(order_models.Order.total_amount).label('total_revenue'),
            func.avg(order_models.Order.total_amount).label('avg_order_value')
        ).filter(
            order_models.Order.order_date >= start_date,
            order_models.Order.order_date <= end_date,
            order_models.Order.status == 'completed'
        ).first()
        
        # Популярные блюда
        popular_dishes = db.query(
            dish_models.Dish.id,
            dish_models.Dish.name,
            func.sum(order_item_models.OrderItem.quantity).label('total_quantity'),
            func.sum(order_item_models.OrderItem.item_total).label('total_revenue')
        ).join(
            order_item_models.OrderItem,
            dish_models.Dish.id == order_item_models.OrderItem.dish_id
        ).join(
            order_models.Order,
            order_item_models.OrderItem.order_id == order_models.Order.id  # Исправлено: order_id -> id
        ).filter(
            order_models.Order.order_date >= start_date,
            order_models.Order.order_date <= end_date,
            order_models.Order.status == 'completed'
        ).group_by(
            dish_models.Dish.id,
            dish_models.Dish.name
        ).order_by(
            desc('total_quantity')
        ).limit(10).all()
        
        popular_dishes_list = [
            PopularDish(
                dish_id=dish.id,
                name=dish.name,
                total_quantity=dish.total_quantity or 0,
                total_revenue=float(dish.total_revenue or 0)
            )
            for dish in popular_dishes
        ]
        
        return SalesReport(
            period=f"{start_date} - {end_date}",
            total_revenue=float(stats.total_revenue or 0),
            total_orders=stats.total_orders or 0,
            average_order_value=float(stats.avg_order_value or 0),
            popular_dishes=popular_dishes_list
        )
    
    @staticmethod
    def get_category_report(db: Session, start_date: date, end_date: date) -> Dict[str, Any]:
        """Отчет по категориям за период"""
        revenue_by_category = db.query(
            category_models.Category.name,
            func.sum(order_item_models.OrderItem.item_total).label('revenue')
        ).join(
            dish_models.Dish,
            category_models.Category.id == dish_models.Dish.category_id
        ).join(
            order_item_models.OrderItem,
            dish_models.Dish.id == order_item_models.OrderItem.dish_id
        ).join(
            order_models.Order,
            order_item_models.OrderItem.order_id == order_models.Order.id  # Исправлено
        ).filter(
            order_models.Order.order_date >= start_date,
            order_models.Order.order_date <= end_date,
            order_models.Order.status == 'completed'
        ).group_by(
            category_models.Category.id,
            category_models.Category.name
        ).all()
        
        total_revenue = sum(item.revenue or 0 for item in revenue_by_category)
        
        category_list = [
            RevenueByCategory(
                category_name=item.name,
                revenue=float(item.revenue or 0),
                percentage=float(item.revenue or 0) / total_revenue * 100 if total_revenue > 0 else 0
            )
            for item in revenue_by_category
        ]
        
        return {
            "period": f"{start_date} - {end_date}",
            "total_revenue": float(total_revenue),
            "revenue_by_category": category_list
        }
    
    @staticmethod
    def get_daily_revenue_report(db: Session, days: int = 30) -> Dict[str, Any]:
        """Отчет по ежедневной выручке за последние N дней"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        daily_revenues = db.query(
            func.date(order_models.Order.order_date).label('date'),
            func.sum(order_models.Order.total_amount).label('revenue'),
            func.count(order_models.Order.id).label('orders')  # Исправлено
        ).filter(
            order_models.Order.order_date >= start_date,
            order_models.Order.order_date <= end_date,
            order_models.Order.status == 'completed'
        ).group_by(
            func.date(order_models.Order.order_date)
        ).order_by(
            func.date(order_models.Order.order_date)
        ).all()
        
        daily_list = [
            DailyRevenue(
                date=item.date,
                revenue=float(item.revenue or 0),
                orders=item.orders or 0
            )
            for item in daily_revenues
        ]
        
        return {
            "period": f"{start_date} - {end_date}",
            "daily_revenues": daily_list
        }
