import pytest
from decimal import Decimal
from backend.src.models import Dish, Category
import uuid

class TestDishModel:
    """Тесты модели Dish"""
    
    def test_create_dish(self, db_session, create_test_category):
        """Тест создания блюда"""
        # Arrange
        category = create_test_category()
        dish_id = str(uuid.uuid4())
        dish_name = "Котлета с пюре"
        dish_price = Decimal("150.00")
        
        # Act
        dish = Dish(
            dish_id=dish_id,
            name=dish_name,
            price=dish_price,
            category_id=category.category_id
        )
        db_session.add(dish)
        db_session.commit()
        db_session.refresh(dish)
        
        # Assert
        assert dish.dish_id == dish_id
        assert dish.name == dish_name
        assert dish.price == dish_price
        assert dish.category_id == category.category_id
        assert dish.category.name == category.name
    
    def test_dish_price_validation(self, db_session, create_test_category):
        """Тест валидации цены блюда"""
        # Arrange
        category = create_test_category()
        
        # Test 1: Положительная цена
        dish1 = Dish(
            dish_id=str(uuid.uuid4()),
            name="Блюдо 1",
            price=Decimal("100.00"),
            category_id=category.category_id
        )
        db_session.add(dish1)
        db_session.commit()
        assert dish1.price > 0
        
        # Test 2: Цена равна 0.01 (минимальная)
        dish2 = Dish(
            dish_id=str(uuid.uuid4()),
            name="Блюдо 2",
            price=Decimal("0.01"),
            category_id=category.category_id
        )
        db_session.add(dish2)
        db_session.commit()
        assert dish2.price == Decimal("0.01")
        

    
    def test_dish_relationships(self, db_session, create_test_dish):
        """Тест связей блюда"""
        # Arrange
        dish = create_test_dish()
        
        # Assert
        assert dish.category is not None
        assert isinstance(dish.category, Category)
        assert dish.category.name == "Тестовая категория"
    
    def test_dish_decimal_precision(self, db_session, create_test_category):
        """Тест точности десятичных значений цены"""
        # Arrange
        category = create_test_category()
        
        # Test с разными десятичными значениями
        test_cases = [
            ("100.00", Decimal("100.00")),
            ("99.99", Decimal("99.99")),
            ("150.50", Decimal("150.50")),
            ("0.01", Decimal("0.01")),
            ("9999.99", Decimal("9999.99")),
        ]
        
        for price_str, expected_decimal in test_cases:
            dish = Dish(
                dish_id=str(uuid.uuid4()),
                name=f"Блюдо за {price_str}",
                price=Decimal(price_str),
                category_id=category.category_id
            )
            db_session.add(dish)
            db_session.commit()
            db_session.refresh(dish)
            
            assert dish.price == expected_decimal
            # Проверяем, что сохранилось 2 знака после запятой
            assert str(dish.price) == price_str
