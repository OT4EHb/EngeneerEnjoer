import pytest
from datetime import datetime
from backend.src.models import Category
import uuid

class TestCategoryModel:
    """Тесты модели Category"""
    
    def test_create_category(self, db_session):
        """Тест создания категории"""
        # Arrange
        category_id = str(uuid.uuid4())
        category_name = "Напитки"
        
        # Act
        category = Category(
            category_id=category_id,
            name=category_name
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        
        # Assert
        assert category.category_id == category_id
        assert category.name == category_name
        assert isinstance(category.category_id, str)
        assert len(category.category_id) == 36  # Длина UUID
    
    def test_category_relationships(self, db_session, create_test_category, create_test_dish):
        """Тест связей категории с блюдами"""
        # Arrange
        category = create_test_category("Супы")
        
        # Act
        dish1 = create_test_dish("Борщ", 120.00, category)
        dish2 = create_test_dish("Щи", 110.00, category)
        
        # Assert
        assert len(category.dishes) == 2
        assert category.dishes[0].name == "Борщ"
        assert category.dishes[1].name == "Щи"
        assert category.dishes[0].category_id == category.category_id
    
   
    def test_category_name_not_null(self, db_session):
        """Тест обязательности имени категории"""
        # Arrange & Act & Assert
        with pytest.raises(Exception):
            category = Category(
                category_id=str(uuid.uuid4()),
                name=None
            )
            db_session.add(category)
            db_session.commit()
    
    @pytest.mark.parametrize("category_name", [
        "Супы",
        "Основные блюда",
        "Напитки",
        "Десерты",
        "123",  # Числа как строка
        "Категория с пробелами",
    ])
    def test_category_name_valid_values(self, db_session, category_name):
        """Тест валидных значений имени категории"""
        # Arrange & Act
        category = Category(
            category_id=str(uuid.uuid4()),
            name=category_name
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        
        # Assert
        assert category.name == category_name
