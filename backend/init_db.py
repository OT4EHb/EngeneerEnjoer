#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных в Docker контейнере
"""

import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.database import engine, Base, SessionLocal
from src.models import Category, Dish
import uuid

def init_database():
    """Инициализация базы данных с тестовыми данными"""
    print("=" * 50)
    print("🛠️  Инициализация базы данных")
    print("=" * 50)
    
    # Создаем таблицы
    print("📦 Создание таблиц...")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы")
    
    db = SessionLocal()
    
    try:
        # Проверяем, есть ли уже данные
        category_count = db.query(Category).count()
        
        if category_count > 0:
            print("ℹ️  База данных уже содержит данные. Пропускаем добавление тестовых данных.")
            return
        
        print("📝 Добавление тестовых данных...")
        
        # Создаем категории
        categories_data = [
            {"name": "Супы"},
            {"name": "Основные блюда"},
            {"name": "Салаты"},
            {"name": "Напитки"},
            {"name": "Десерты"},
        ]
        
        categories = []
        for cat_data in categories_data:
            category = Category(
                category_id=str(uuid.uuid4()),
                name=cat_data["name"]
            )
            db.add(category)
            categories.append(category)
        
        db.commit()
        
        # Получаем ID категорий
        cat_map = {cat.name: cat.category_id for cat in categories}
        
        # Создаем блюда
        dishes_data = [
            {"name": "Борщ", "price": 120.50, "category": "Супы"},
            {"name": "Суп куриный", "price": 100.00, "category": "Супы"},
            {"name": "Котлета с пюре", "price": 150.00, "category": "Основные блюда"},
            {"name": "Гречка с грибами", "price": 130.00, "category": "Основные блюда"},
            {"name": "Плов", "price": 160.00, "category": "Основные блюда"},
            {"name": "Оливье", "price": 90.00, "category": "Салаты"},
            {"name": "Овощной салат", "price": 70.00, "category": "Салаты"},
            {"name": "Чай", "price": 30.00, "category": "Напитки"},
            {"name": "Кофе", "price": 50.00, "category": "Напитки"},
            {"name": "Компот", "price": 40.00, "category": "Напитки"},
            {"name": "Морс", "price": 45.00, "category": "Напитки"},
            {"name": "Торт", "price": 80.00, "category": "Десерты"},
            {"name": "Пирожное", "price": 60.00, "category": "Десерты"},
        ]
        
        for dish_data in dishes_data:
            dish = Dish(
                dish_id=str(uuid.uuid4()),
                name=dish_data["name"],
                price=dish_data["price"],
                category_id=cat_map[dish_data["category"]]
            )
            db.add(dish)
        
        db.commit()
        print(f"✅ Добавлено {len(categories)} категорий и {len(dishes_data)} блюд")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
