import pytest
from pydantic import ValidationError
from backend.src.schemas.order import (
    OrderItemCreate, 
    OrderCreate, 
    OrderItemResponse, 
    OrderResponse
)

class TestOrderSchemas:
    """Тесты схем заказов"""
    
    def test_order_item_create_valid(self):
        """Тест валидного создания позиции заказа"""
        # Arrange
        item_data = {
            "dish_id": "123e4567-e89b-12d3-a456-426614174000",
            "quantity": 2
        }
        
        # Act
        order_item = OrderItemCreate(**item_data)
        
        # Assert
        assert order_item.dish_id == "123e4567-e89b-12d3-a456-426614174000"
        assert order_item.quantity == 2

    
    def test_order_create_valid(self):
        """Тест валидного создания заказа"""
        # Arrange
        order_data = {
            "items": [
                {
                    "dish_id": "dish-uuid-1",
                    "quantity": 2
                },
                {
                    "dish_id": "dish-uuid-2",
                    "quantity": 1
                }
            ]
        }
        
        # Act
        order = OrderCreate(**order_data)
        
        # Assert
        assert len(order.items) == 2
        assert order.items[0].dish_id == "dish-uuid-1"
        assert order.items[0].quantity == 2
        assert order.items[1].dish_id == "dish-uuid-2"
        assert order.items[1].quantity == 1
    
    def test_order_item_response_valid(self):
        """Тест валидного ответа с позицией заказа"""
        # Arrange
        item_data = {
            "dish_name": "Борщ",
            "quantity": 2,
            "price_per_item": 120.50,
            "item_total": 241.00
        }
        
        # Act
        order_item = OrderItemResponse(**item_data)
        
        # Assert
        assert order_item.dish_name == "Борщ"
        assert order_item.quantity == 2
        assert order_item.price_per_item == 120.50
        assert order_item.item_total == 241.00
    
    def test_order_response_valid(self):
        """Тест валидного ответа с заказом"""
        # Arrange
        from datetime import datetime
        
        order_data = {
            "order_id": "order-uuid-123",
            "order_date": datetime.now(),
            "total_amount": 350.50,
            "items": [
                {
                    "dish_name": "Борщ",
                    "quantity": 2,
                    "price_per_item": 120.50,
                    "item_total": 241.00
                },
                {
                    "dish_name": "Компот",
                    "quantity": 1,
                    "price_per_item": 40.00,
                    "item_total": 40.00
                }
            ]
        }
        
        # Act
        order = OrderResponse(**order_data)
        
        # Assert
        assert order.order_id == "order-uuid-123"
        assert isinstance(order.order_date, datetime)
        assert order.total_amount == 350.50
        assert len(order.items) == 2
        assert order.items[0].dish_name == "Борщ"
        assert order.items[1].dish_name == "Компот"
    
    @pytest.mark.parametrize("valid_quantity", [1, 2, 10, 100, 999])
    def test_order_item_quantity_valid_cases(self, valid_quantity):
        """Тест различных валидных количеств"""
        # Arrange & Act
        order_item = OrderItemCreate(
            dish_id="test-uuid",
            quantity=valid_quantity
        )
        
        # Assert
        assert order_item.quantity == valid_quantity
 
    def test_order_items_validation(self):
        """Тест валидации списка позиций"""
        # Test 1: Одна позиция
        order1 = OrderCreate(items=[{"dish_id": "test1", "quantity": 1}])
        assert len(order1.items) == 1
        
        # Test 2: Много позиций
        items = [{"dish_id": f"dish{i}", "quantity": i} for i in range(1, 6)]
        order2 = OrderCreate(items=items)
        assert len(order2.items) == 5
        
        # Test 3: Дубликаты dish_id разрешены
        order3 = OrderCreate(items=[
            {"dish_id": "same-dish", "quantity": 1},
            {"dish_id": "same-dish", "quantity": 2}
        ])
        assert len(order3.items) == 2
        assert order3.items[0].dish_id == order3.items[1].dish_id
    
    def test_order_response_config(self):
        """Тест конфигурации схемы OrderResponse"""
        # Arrange
        from datetime import datetime
        
        order_data = {
            "order_id": "test-uuid",
            "order_date": datetime.now(),
            "total_amount": 100.00,
            "items": []
        }
        
        # Act
        order = OrderResponse(**order_data)
        
        # Assert
        # Проверяем, что схема поддерживает from_attributes
        assert hasattr(order.Config, 'from_attributes')
        assert order.Config.from_attributes is True
