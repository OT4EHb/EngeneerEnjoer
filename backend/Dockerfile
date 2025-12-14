FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY backend/ .

# Создаем структуру
RUN mkdir -p /app/src

# Запускаем приложение
CMD ["python", "main.py"]
