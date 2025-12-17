import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Добавляем путь к проекту
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# ВАЖНО: Сначала импортируем Base
from backend.src.database import Base

# ВАЖНО: Затем импортируем ВСЕ модели
from backend.src.models import Category, Dish, Order, OrderItem

# Создаем тестовый engine
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

from backend.src.main import app
from backend.src.database import get_db
import uuid
from datetime import datetime

@pytest.fixture(scope="function")
def db_session():
    """Создание тестовой сессии БД"""

    Base.metadata.create_all(bind=test_engine)
      
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Тестовый клиент FastAPI"""
    print(f"\n[client fixture] Переопределяем get_db")
    print(f"[client fixture] db_session.bind: {db_session.bind.url}")
    
    def override_get_db():
        print(f"[override_get_db] Вызывается dependency")
        try:
            yield db_session
        finally:
            print(f"[override_get_db] Завершено")
    
    # Проверяем что переопределяем правильную зависимость
    print(f"[client fixture] get_db: {get_db}")
    print(f"[client fixture] app.dependency_overrides до: {app.dependency_overrides}")
    
    app.dependency_overrides[get_db] = override_get_db
    
    print(f"[client fixture] app.dependency_overrides после: {app.dependency_overrides}")
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
    print(f"[client fixture] Очищены overrides")

@pytest.fixture(scope="function", autouse=True)
def ensure_tables_created(db_session):
    """Автоматически создает таблицы перед каждым тестом"""
    # Таблицы уже созданы в db_session фикстуре
    # Но на всякий случай проверяем
    from sqlalchemy import inspect
    inspector = inspect(db_session.bind)
    tables = inspector.get_table_names()
    
    if 'orders' not in tables:
        print(f"Таблицы отсутствуют: {tables}. Создаем...")
        from backend.src.database import Base
        Base.metadata.create_all(bind=db_session.bind)
        tables = inspector.get_table_names()
        print(f"Таблицы после создания: {tables}")
    
    yield

# Фикстуры для тестовых данных
@pytest.fixture
def test_category_data():
    """Тестовые данные категории"""
    return {
        "name": "Супы"
    }

@pytest.fixture
def test_dish_data():
    """Тестовые данные блюда"""
    return {
        "name": "Борщ",
        "price": 120.50,
        "category_id": str(uuid.uuid4())
    }

@pytest.fixture
def test_order_data():
    """Тестовые данные заказа"""
    return {
        "items": [
            {
                "dish_id": str(uuid.uuid4()),
                "quantity": 2
            }
        ]
    }

@pytest.fixture
def create_test_category(db_session):
    """Создание тестовой категории в БД"""
    def _create_category(name="Тестовая категория"):
        category = Category(
            category_id=str(uuid.uuid4()),
            name=name
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return category
    return _create_category

@pytest.fixture
def create_test_dish(db_session, create_test_category):
    """Создание тестового блюда в БД"""
    def _create_dish(name="Тестовое блюдо", price=100.00, category=None):
        if not category:
            category = create_test_category()
        
        dish = Dish(
            dish_id=str(uuid.uuid4()),
            name=name,
            price=price,
            category_id=category.category_id
        )
        db_session.add(dish)
        db_session.commit()
        db_session.refresh(dish)
        return dish
    return _create_dish

@pytest.fixture
def create_test_order(db_session, create_test_dish):
    """Создание тестового заказа в БД"""
    def _create_order(total_amount=250.00):
        dish = create_test_dish()
        
        order = Order(
            order_id=str(uuid.uuid4()),
            total_amount=total_amount
        )
        db_session.add(order)
        db_session.commit()
        
        # Добавляем позицию заказа
        order_item = OrderItem(
            order_item_id=str(uuid.uuid4()),
            order_id=order.order_id,
            dish_id=dish.dish_id,
            quantity=2,
            item_total=200.00
        )
        db_session.add(order_item)
        db_session.commit()
        db_session.refresh(order)
        
        return order, dish
    return _create_order

# Фикстура для асинхронных тестов
@pytest.fixture
def anyio_backend():
    return 'asyncio'
