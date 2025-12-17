# load_testing/create_test_db.py
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.src.database import Base
from backend.src.models import Category, Dish, Order, OrderItem
import uuid
from datetime import datetime, timedelta
import random
import shutil

def create_test_database(data_sizes=[10, 100, 1000, 10000]):
    """Создание тестовых баз данных разных размеров"""
    
    # Создаем папку для тестовых БД
    os.makedirs("test_databases", exist_ok=True)
    
    for size in data_sizes:
        print(f"\n{'='*60}")
        print(f"Создание БД с {size} записями...")
        print(f"{'='*60}")
        
        # Создаем файл БД
        db_path = f"test_databases/test_{size}.db"
        
        # Удаляем старый файл если существует
        if os.path.exists(db_path):
            os.remove(db_path)
        
        # Создаем engine для новой БД
        engine = create_engine(f"sqlite:///{db_path}")
        
        # Создаем таблицы
        Base.metadata.create_all(bind=engine)
        
        # Создаем сессию
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Генерируем данные
        stats = generate_test_data(session, size)
        
        # Сохраняем (коммитим)
        session.commit()
        session.close()
        
        print(f"✓ Создана БД: {db_path}")
        print(f"  - Категорий: {stats['categories']}")
        print(f"  - Блюд: {stats['dishes']}")
        print(f"  - Заказов: {stats['orders']}")
        print(f"  - Позиций заказов: {stats['order_items']}")
        print(f"  - Всего записей: {stats['total']}")
        
        # Проверяем размер файла
        file_size = os.path.getsize(db_path) / 1024  # в КБ
        print(f"  - Размер файла: {file_size:.2f} KB")

def generate_test_data(session, target_size):
    """Генерация тестовых данных"""
    
    stats = {
        'categories': 0,
        'dishes': 0,
        'orders': 0,
        'order_items': 0,
        'total': 0
    }
    
    # 1. Создаем категории (10% от целевого размера, но не менее 2)
    num_categories = max(2, target_size // 10)
    categories = []
    
    for i in range(num_categories):
        category = Category(
            category_id=str(uuid.uuid4()),
            name=f"Категория {i+1}"
        )
        session.add(category)
        categories.append(category)
    
    session.commit()
    stats['categories'] = num_categories
    
    # 2. Создаем блюда (70% от целевого размера)
    num_dishes = max(target_size * 7 // 10, num_categories * 2)
    dishes = []
    
    dish_names = [
        "Борщ", "Щи", "Солянка", "Греческий салат", "Цезарь",
        "Стейк", "Котлета по-киевски", "Плов", "Пельмени", "Пицца",
        "Тирамису", "Чизкейк", "Мороженое", "Кофе", "Чай",
        "Компот", "Морс", "Лимонад", "Пиво", "Вино"
    ]
    
    for i in range(num_dishes):
        dish = Dish(
            dish_id=str(uuid.uuid4()),
            name=f"{random.choice(dish_names)} {i+1}",
            price=round(random.uniform(50, 500), 2),
            category_id=random.choice(categories).category_id
        )
        session.add(dish)
        dishes.append(dish)
    
    session.commit()
    stats['dishes'] = num_dishes
    
    # 3. Создаем заказы (20% от целевого размера)
    num_orders = max(target_size // 5, 10)
    
    customer_names = [
        "Иван Иванов", "Петр Петров", "Анна Сидорова", "Мария Кузнецова",
        "Алексей Смирнов", "Елена Попова", "Дмитрий Васильев", "Ольга Новикова",
        "Сергей Федоров", "Наталья Морозова"
    ]
    
    for i in range(num_orders):
        # Случайная дата за последний год
        days_ago = random.randint(0, 365)
        order_date = datetime.utcnow() - timedelta(days=days_ago)
        
        order = Order(
            order_id=str(uuid.uuid4()),
            total_amount=0,  # Пока 0, посчитаем после добавления позиций
            order_date=order_date
        )
        session.add(order)
        session.flush()  # Получаем ID без коммита
        
        # 4. Добавляем позиции заказа (1-5 позиций)
        num_items = random.randint(1, 5)
        order_items = []
        order_total = 0
        
        for _ in range(num_items):
            dish = random.choice(dishes)
            quantity = random.randint(1, 3)
            item_total = dish.price * quantity
            order_total += item_total
            
            order_item = OrderItem(
                order_item_id=str(uuid.uuid4()),
                order_id=order.order_id,
                dish_id=dish.dish_id,
                quantity=quantity,
                item_total=item_total
            )
            session.add(order_item)
            order_items.append(order_item)
        
        # Обновляем общую сумму заказа
        order.total_amount = order_total
        
        stats['order_items'] += num_items
    
    session.commit()
    stats['orders'] = num_orders
    stats['total'] = stats['categories'] + stats['dishes'] + stats['orders'] + stats['order_items']
    
    return stats

def create_in_memory_database(size):
    """Создание БД в памяти для быстрого тестирования"""
    
    print(f"Создание in-memory БД с {size} записями...")
    
    # Создаем engine для БД в памяти
    engine = create_engine("sqlite:///:memory:")
    
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    # Создаем сессию
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Генерируем данные
    stats = generate_test_data(session, size)
    
    session.commit()
    
    print(f"✓ Создана in-memory БД:")
    print(f"  - Категорий: {stats['categories']}")
    print(f"  - Блюд: {stats['dishes']}")
    print(f"  - Заказов: {stats['orders']}")
    
    return engine, session

def load_test_database_to_app(size, app_db_path="restaurant.db"):
    """Загрузка тестовой БД в приложение"""
    
    print(f"\nЗагрузка БД с {size} записями в приложение...")
    
    source_db = f"test_databases/test_{size}.db"
    
    if not os.path.exists(source_db):
        print(f"❌ Файл {source_db} не найден")
        return False
    
    # Копируем тестовую БД поверх основной
    shutil.copy2(source_db, app_db_path)
    
    print(f"✓ БД загружена в {app_db_path}")
    
    # Проверяем что данные загрузились
    engine = create_engine(f"sqlite:///{app_db_path}")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    from backend.src.models import Category, Dish, Order
    
    categories_count = session.query(Category).count()
    dishes_count = session.query(Dish).count()
    orders_count = session.query(Order).count()
    
    print(f"  - Проверка: {categories_count} категорий, {dishes_count} блюд, {orders_count} заказов")
    
    session.close()
    
    return True

if __name__ == "__main__":
    # Создаем все тестовые БД
    create_test_database([10, 100, 1000, 10000])
    
    print("\n" + "="*60)
    print("ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ:")
    print("="*60)
    print("\nСозданные файлы БД:")
    print("1. test_databases/test_10.db     - 10 записей")
    print("2. test_databases/test_100.db    - 100 записей")
    print("3. test_databases/test_1000.db   - 1000 записей")
    print("4. test_databases/test_10000.db  - 10000 записей")
    
    print("\nКак использовать:")
    print("1. Загрузить БД в приложение:")
    print("   load_test_database_to_app(100)  # Для 100 записей")
    
    print("\n2. Создать in-memory БД для тестов:")
    print("   engine, session = create_in_memory_database(1000)")
