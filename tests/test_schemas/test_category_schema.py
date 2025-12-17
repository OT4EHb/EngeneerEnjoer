import pytest
from pydantic import ValidationError
from backend.src.schemas.category import CategoryCreate, CategoryUpdate, Category

class TestCategorySchemas:
    """Тесты схем категорий"""
    
    def test_category_create_valid(self):
        """Тест валидного создания категории"""
        # Arrange
        category_data = {
            "name": "Напитки"
        }
        
        # Act
        category = CategoryCreate(**category_data)
        
        # Assert
        assert category.name == "Напитки"
      
    
    def test_category_update_valid(self):
        """Тест валидного обновления категории"""
        # Arrange
        update_data = {
            "name": "Обновленное название"
        }
        
        # Act
        category_update = CategoryUpdate(**update_data)
        
        # Assert
        assert category_update.name == "Обновленное название"
    
    def test_category_update_partial(self):
        """Тест частичного обновления категории"""
        # Arrange
        update_data = {
            "name": "Новое название"
        }
        
        # Act
        category_update = CategoryUpdate(**update_data)
        
        # Assert
        assert category_update.name == "Новое название"
    
    def test_category_response_valid(self):
        """Тест валидного ответа с категорией"""
        # Arrange
        category_data = {
            "category_id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Супы"
        }
        
        # Act
        category = Category(**category_data)
        
        # Assert
        assert category.category_id == "123e4567-e89b-12d3-a456-426614174000"
        assert category.name == "Супы"
    
    @pytest.mark.parametrize("valid_name", [
        "Супы",
        "Основные блюда",
        "Напитки 123",
        "Категория-тест",
        "Категория с пробелами",
    ])
    def test_category_name_valid_cases(self, valid_name):
        """Тест различных валидных имен категорий"""
        # Arrange & Act
        category = CategoryCreate(name=valid_name)
        
        # Assert
        assert category.name == valid_name
    
 
    def test_category_schema_config(self):
        """Тест конфигурации схемы"""
        # Arrange
        category_data = {
            "category_id": "test-uuid",
            "name": "Тест"
        }
        
        # Act
        category = Category(**category_data)
        
        # Assert
        # Проверяем, что схема поддерживает from_attributes (бывший orm_mode)
        assert hasattr(category.Config, 'from_attributes')
        assert category.Config.from_attributes is True
