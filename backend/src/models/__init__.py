# Экспортируем все модели для удобного импорта
from .category import Category
from .dish import Dish
from .order import Order
from .order_item import OrderItem

__all__ = ["Category", "Dish", "Order", "OrderItem"]
