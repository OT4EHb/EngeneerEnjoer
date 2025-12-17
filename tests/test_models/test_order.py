import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from backend.src.models import Order, OrderItem
import uuid

class TestOrderModel:
    """Тесты модели Order"""
    
    def test_create_order(self, db_session):
        """Тест создания заказа"""
        # Arrange
        order_id = str(uuid.uuid4())
        
        # Act
        order = Order(
            order_id=order_id,
            total_amount=Decimal("250.00")
        )
        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)
        
        # Assert
        assert order.order_id == order_id
        assert order.total_amount == Decimal("250.00")
        assert order.order_date is not None
        assert isinstance(order.order_date, datetime)
    
    def test_order_default_values(self, db_session):
        """Тест значений по умолчанию"""
        # Arrange & Act
        order = Order(
            order_id=str(uuid.uuid4())
            # total_amount должен установиться в 0.00 по умолчанию
        )
        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)
        
        # Assert
        assert order.total_amount == Decimal("0.00")
        assert order.order_date is not None
        # Проверяем, что время установлено (московское, UTC+3)
        assert order.order_date > datetime.utcnow() - timedelta(minutes=1)
    
    def test_order_total_amount_validation(self, db_session):
        """Тест валидации суммы заказа"""
        # Test 1: Положительная сумма
        order1 = Order(
            order_id=str(uuid.uuid4()),
            total_amount=Decimal("100.00")
        )
        db_session.add(order1)
        db_session.commit()
        assert order1.total_amount == Decimal("100.00")
        
        # Test 2: Сумма равна 0
        order2 = Order(
            order_id=str(uuid.uuid4()),
            total_amount=Decimal("0.00")
        )
        db_session.add(order2)
        db_session.commit()
        assert order2.total_amount == Decimal("0.00")
     
    
    def test_order_relationships(self, db_session, create_test_order):
        """Тест связей заказа"""
        # Arrange
        order, dish = create_test_order()
        
        # Act
        order_items = db_session.query(OrderItem).filter(
            OrderItem.order_id == order.order_id
        ).all()
        
        # Assert
        assert len(order.items) == 1
        assert order.items[0].dish_id == dish.dish_id
        assert order.items[0].quantity == 2
        assert order.items[0].item_total == Decimal("200.00")
    
    def test_order_cascade_delete(self, db_session, create_test_order):
        """Тест каскадного удаления позиций заказа"""
        # Arrange
        order, dish = create_test_order()
        order_id = order.order_id
        
        # Проверяем, что позиция существует
        order_items_before = db_session.query(OrderItem).filter(
            OrderItem.order_id == order_id
        ).count()
        assert order_items_before == 1
        
        # Act: Удаляем заказ
        db_session.delete(order)
        db_session.commit()
        
        # Assert: Позиция заказа тоже должна удалиться
        order_items_after = db_session.query(OrderItem).filter(
            OrderItem.order_id == order_id
        ).count()
        assert order_items_after == 0
    
    def test_order_date_timezone(self, db_session):
        """Тест временной зоны заказа"""
        # Arrange & Act
        order = Order(
            order_id=str(uuid.uuid4()),
            total_amount=Decimal("100.00")
        )
        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)
        
        # Assert
        # Проверяем, что время установлено (должно быть UTC+3)
        utc_now = datetime.utcnow()
        moscow_time = order.order_date
        
        # Разница должна быть примерно 3 часа
        time_diff = moscow_time - utc_now
        assert timedelta(hours=2.9) < time_diff < timedelta(hours=3.1)
    

