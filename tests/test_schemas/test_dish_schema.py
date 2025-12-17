import pytest
from decimal import Decimal
from pydantic import ValidationError
from backend.src.schemas.dish import DishCreate, DishUpdate, Dish

class TestDishSchemas:
    """Тесты схем блюд"""
    
    def test_dish_create_valid(self):
        """Тест валидного создания блюда"""
        # Arrange
        dish_data = {
            "name": "Борщ",
            "price": Decimal("120.50"),
            "category_id": "123e4567-e89b-12d3-a456-426614174000"
        }
        
        # Act
        dish = DishCreate(**dish_data)
        
        # Assert
        assert dish.name == "Борщ"
        assert dish.price == Decimal("120.50")
        assert dish.category_id == "123e4567-e89b-12d3-a456-426614174000"
       
    def test_dish_update_valid(self):
        """Тест валидного обновления блюда"""
        # Arrange
        update_data = {
            "name": "Обновленный борщ",
            "price": Decimal("130.00"),
            "category_id": "new-category-uuid"
        }
        
        # Act
        dish_update = DishUpdate(**update_data)
        
        # Assert
        assert dish_update.name == "Обновленный борщ"
        assert dish_update.price == Decimal("130.00")
        assert dish_update.category_id == "new-category-uuid"
    
    def test_dish_update_partial(self):
        """Тест частичного обновления блюда"""
        # Test 1: Только имя
        update1 = DishUpdate(name="Новое имя")
        assert update1.name == "Новое имя"
        assert update1.price is None
        assert update1.category_id is None
        
        # Test 2: Только цена
        update2 = DishUpdate(price=Decimal("150.00"))
        assert update2.name is None
        assert update2.price == Decimal("150.00")
        assert update2.category_id is None
        
        # Test 3: Только категория
        update3 = DishUpdate(category_id="new-cat-uuid")
        assert update3.name is None
        assert update3.price is None
        assert update3.category_id == "new-cat-uuid"
    
    def test_dish_response_valid(self):
        """Тест валидного ответа с блюдом"""
        # Arrange
        dish_data = {
            "dish_id": "dish-uuid-123",
            "name": "Котлета с пюре",
            "price": Decimal("150.00"),
            "category_id": "category-uuid-456"
        }
        
        # Act
        dish = Dish(**dish_data)
        
        # Assert
        assert dish.dish_id == "dish-uuid-123"
        assert dish.name == "Котлета с пюре"
        assert dish.price == Decimal("150.00")
        assert dish.category_id == "category-uuid-456"
    
    def test_dish_price_decimal_precision(self):
        """Тест точности десятичных значений цены"""
        test_cases = [
            ("100.00", Decimal("100.00")),
            ("99.99", Decimal("99.99")),
            ("150.50", Decimal("150.50")),
            ("0.01", Decimal("0.01")),
            ("9999.99", Decimal("9999.99")),
        ]
        
        for price_str, expected_decimal in test_cases:
            dish = DishCreate(
                name=f"Блюдо за {price_str}",
                price=Decimal(price_str),
                category_id="test-uuid"
            )
            assert dish.price == expected_decimal
            # Проверяем, что сохранилось 2 знака после запятой
            assert str(dish.price) == price_str
    
    @pytest.mark.parametrize("valid_price", [
        Decimal("0.01"),  # Минимальная цена
        Decimal("1.00"),
        Decimal("99.99"),
        Decimal("100.00"),
        Decimal("9999.99"),  # Большая цена
    ])
    def test_dish_price_valid_cases(self, valid_price):
        """Тест различных валидных цен"""
        # Arrange & Act
        dish = DishCreate(
            name="Тестовое блюдо",
            price=valid_price,
            category_id="test-uuid"
        )
        
        # Assert
        assert dish.price == valid_price
   
    
    def test_dish_schema_config(self):
        """Тест конфигурации схемы"""
        # Arrange
        dish_data = {
            "dish_id": "test-uuid",
            "name": "Тест",
            "price": Decimal("100.00"),
            "category_id": "category-uuid"
        }
        
        # Act
        dish = Dish(**dish_data)
        
        # Assert
        # Проверяем, что схема поддерживает from_attributes
        assert hasattr(dish.Config, 'from_attributes')
        assert dish.Config.from_attributes is True
