import pytest
from decimal import Decimal
from backend.src.models import OrderItem, Order, Dish
import uuid

class TestOrderItemModel:
    """Тесты модели OrderItem"""
    
    def test_create_order_item(self, db_session, create_test_category, create_test_dish):
        """Тест создания позиции заказа"""
        # Arrange
        category = create_test_category()
        dish = create_test_dish(category=category)
        order = Order(
            order_id=str(uuid.uuid4()),
            total_amount=Decimal("0.00")
        )
        db_session.add(order)
        db_session.commit()
        
        order_item_id = str(uuid.uuid4())
        
        # Act
        order_item = OrderItem(
            order_item_id=order_item_id,
            order_id=order.order_id,
            dish_id=dish.dish_id,
            quantity=3,
            item_total=Decimal("300.00")
        )
        db_session.add(order_item)
        db_session.commit()
        db_session.refresh(order_item)
        
        # Assert
        assert order_item.order_item_id == order_item_id
        assert order_item.order_id == order.order_id
        assert order_item.dish_id == dish.dish_id
        assert order_item.quantity == 3
        assert order_item.item_total == Decimal("300.00")
    
    def test_order_item_quantity_validation(self, db_session, create_test_order):
        """Тест валидации количества"""
        # Arrange
        order, dish = create_test_order()
        
        # Test 1: Положительное количество
        order_item1 = OrderItem(
            order_item_id=str(uuid.uuid4()),
            order_id=order.order_id,
            dish_id=dish.dish_id,
            quantity=1,
            item_total=Decimal("100.00")
        )
        db_session.add(order_item1)
        db_session.commit()
        assert order_item1.quantity == 1
        
        # Test 2: Большое количество
        order_item2 = OrderItem(
            order_item_id=str(uuid.uuid4()),
            order_id=order.order_id,
            dish_id=dish.dish_id,
            quantity=100,
            item_total=Decimal("10000.00")
        )
        db_session.add(order_item2)
        db_session.commit()
        assert order_item2.quantity == 100
        
    
    def test_order_item_total_validation(self, db_session, create_test_order):
        """Тест валидации суммы позиции"""
        # Arrange
        order, dish = create_test_order()
        
        order_item1 = OrderItem(
            order_item_id=str(uuid.uuid4()),
            order_id=order.order_id,
            dish_id=dish.dish_id,
            quantity=2,
            item_total=Decimal("200.00")
        )
        db_session.add(order_item1)
        db_session.commit()
        assert order_item1.item_total == Decimal("200.00")
       
    
    def test_order_item_relationships(self, db_session, create_test_order):
        """Тест связей позиции заказа"""
        # Arrange
        order, dish = create_test_order()
        
        # Создаем позицию заказа
        order_item = OrderItem(
            order_item_id=str(uuid.uuid4()),
            order_id=order.order_id,
            dish_id=dish.dish_id,
            quantity=2,
            item_total=Decimal("200.00")
        )
        db_session.add(order_item)
        db_session.commit()
        db_session.refresh(order_item)
        
        # Assert
        assert order_item.order is not None
        assert isinstance(order_item.order, Order)
        assert order_item.order.order_id == order.order_id
        
        assert order_item.dish is not None
        assert isinstance(order_item.dish, Dish)
        assert order_item.dish.dish_id == dish.dish_id
        assert order_item.dish.name == dish.name
    
    def test_order_item_calculation(self, db_session, create_test_dish):
        """Тест расчета суммы позиции"""
        # Arrange
        dish = create_test_dish(price=Decimal("120.50"))
        order = Order(
            order_id=str(uuid.uuid4()),
            total_amount=Decimal("0.00")
        )
        db_session.add(order)
        db_session.commit()
        
        # Act
        quantity = 3
        expected_total = dish.price * quantity
        
        order_item = OrderItem(
            order_item_id=str(uuid.uuid4()),
            order_id=order.order_id,
            dish_id=dish.dish_id,
            quantity=quantity,
            item_total=expected_total
        )
        db_session.add(order_item)
        db_session.commit()
        db_session.refresh(order_item)
        
        # Assert
        assert order_item.item_total == expected_total
        assert order_item.item_total == Decimal("361.50")  # 120.50 * 3

