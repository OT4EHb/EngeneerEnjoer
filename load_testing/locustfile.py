# load_testing/locustfile.py
from locust import HttpUser, task, between, TaskSet
import random
import string
import json
from datetime import datetime, timedelta

def generate_random_string(length=10):
    """Генерация случайной строки"""
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

def generate_random_phone():
    """Генерация случайного номера телефона"""
    return f"+7{random.randint(900, 999)}{random.randint(100, 999)}{random.randint(10, 99)}{random.randint(10, 99)}"

class AdminTasks(TaskSet):
    """Задачи администратора (CRUD операции)"""
    
    def on_start(self):
        """Выполняется при старте каждого пользователя"""
        # Получаем список категорий для использования в других запросах
        self.categories = []
        response = self.client.get("/static/admin.html")
        if response.status_code == 200:
            self.categories = response.json()
    
    @task(5)
    def get_categories(self):
        """Получение списка категорий (самый частый запрос)"""
        self.client.get("/api/admin/categories")
    
    @task(5)
    def get_dishes(self):
        """Получение списка блюд"""
        self.client.get("/api/admin/dishes")
    
    @task(4)
    def get_orders_by_date(self):
        """Получение заказов по дате"""
        # Генерируем случайные даты
        end_date = datetime.now()
        start_date = end_date - timedelta(days=random.randint(1, 30))
        
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        self.client.get("/api/admin/orders/by-date", params=params)
    
   
    
    @task(2)
    def create_category(self):
        """Создание новой категории"""
        data = {"name": f"Категория {generate_random_string(5)}"}
        self.client.post("/api/admin/categories", json=data)
    
    @task(2)
    def create_dish(self):
        """Создание нового блюда"""
        if self.categories:
            category = random.choice(self.categories)
            data = {
                "name": f"Блюдо {generate_random_string(6)}",
                "price": round(random.uniform(50, 500), 2),
                "category_id": category["category_id"]
            }
            self.client.post("/api/admin/dishes", json=data)
    
    @task(1)
    def create_order(self):
        """Создание нового заказа (самый редкий и сложный запрос)"""
        # Сначала получаем список блюд
        response = self.client.get("/api/admin/dishes")
        if response.status_code == 200 and response.json():
            dishes = response.json()
            
            # Выбираем 1-3 случайных блюда
            selected_dishes = random.sample(dishes, min(3, len(dishes)))
            
            # Формируем позиции заказа
            items = []
            for dish in selected_dishes:
                items.append({
                    "dish_id": dish["dish_id"],
                    "quantity": random.randint(1, 3)
                })
            
            # Данные заказа
            order_data = {
                "customer_name": f"Клиент {generate_random_string(6)}",
                "customer_phone": generate_random_phone(),
                "items": items
            }
            
            self.client.post("/api/cashier/orders/today", json=order_data)

class PublicTasks(TaskSet):
    """Задачи публичной части API (меню)"""
    
    @task(10)
    def get_public_menu(self):
        """Получение публичного меню (самый частый запрос)"""
        self.client.get("/api/cashier/menu")
    
    @task(3)
    def get_categories_public(self):
        """Получение категорий для меню"""
        self.client.get("/api/cashier/orders/today")
    

class WebsiteUser(HttpUser):
    """
    Виртуальный пользователь для нагрузочного тестирования.
    
    Настройки:
    - wait_time: время между запросами (1-3 секунды)
    - tasks: какие задачи выполняет пользователь
    - weight: вероятность выбора этого класса пользователя
    """
    wait_time = between(1, 3)  # Ожидание 1-3 секунды между запросами
    tasks = [AdminTasks, PublicTasks]  # Может выполнять обе задачи
    weight = 3  # Вероятность выбора этого пользователя

class AdminUser(HttpUser):
    """Пользователь-администратор (только админские задачи)"""
    wait_time = between(2, 5)  # Админы работают медленнее
    tasks = [AdminTasks]
    weight = 1  # Меньше администраторов, чем обычных пользователей

class PublicUser(HttpUser):
    """Публичный пользователь (только просмотр меню)"""
    wait_time = between(0.5, 2)  # Быстро листают меню
    tasks = [PublicTasks]
    weight = 5  # Больше всего публичных пользователей
