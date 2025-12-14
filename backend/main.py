#!/usr/bin/env python3
"""
Точка входа для запуска FastAPI приложения
"""

import uvicorn
import os
import sys

# Добавляем путь к src в sys.path для абсолютных импортов
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, current_dir)
sys.path.insert(0, src_path)

if __name__ == "__main__":
    # Получаем настройки из переменных окружения
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    print("=" * 50)
    print(f"🚀 Запуск сервера столовой")
    print(f"📡 Адрес: {host}:{port}")
    print(f"📁 Рабочая директория: {os.getcwd()}")
    print(f"🔧 Режим отладки: {debug}")
    print(f"🐍 Python путь: {sys.path}")
    print("=" * 50)
    
    # Запускаем сервер
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=debug,  # Автоперезагрузка только в режиме отладки
        log_level="info"
    )
