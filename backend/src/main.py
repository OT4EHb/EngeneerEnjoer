from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os

# Используем абсолютные импорты
from src.database import engine, Base, create_tables
from src.api import admin, cashier, reports

# Создаем таблицы при старте
create_tables()

# Создаем экземпляр приложения
app = FastAPI(
    title="Столовая API",
    description="API для системы управления заказами в столовой",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(cashier.router, prefix="/api/cashier", tags=["Кассир"])
app.include_router(admin.router, prefix="/api/admin", tags=["Администратор"])
app.include_router(reports.router, prefix="/api/reports", tags=["Отчеты"])

# Путь к фронтенду
FRONTEND_PATH = os.path.join(os.path.dirname(__file__), "../../frontend")

# Проверяем существование фронтенда и монтируем статические файлы
if os.path.exists(FRONTEND_PATH):
    app.mount("/static", StaticFiles(directory=FRONTEND_PATH), name="static")
    
    @app.get("/")
    async def serve_frontend():
        """Сервим главную страницу кассира"""
        return FileResponse(os.path.join(FRONTEND_PATH, "index.html"))
    
    @app.get("/admin")
    async def serve_admin():
        """Сервим страницу администратора"""
        return FileResponse(os.path.join(FRONTEND_PATH, "admin.html"))
    
    @app.get("/reports")
    async def serve_reports():
        """Сервим страницу отчетов"""
        return FileResponse(os.path.join(FRONTEND_PATH, "reports.html"))
else:
    print("⚠️  Фронтенд не найден. API доступен, но статические файлы не будут обслуживаться.")

# Маршрут для проверки здоровья
@app.get("/health")
async def health_check():
    """Проверка работоспособности сервиса"""
    import sqlite3
    
    try:
        # Проверяем подключение к базе данных
        db_path = os.path.join(os.path.dirname(__file__), "../../instance/canteen.db")
        
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            conn.execute("SELECT 1")
            conn.close()
            db_status = "connected"
        else:
            db_status = "database_not_created"
            
        return JSONResponse({
            "status": "healthy",
            "service": "canteen-api",
            "database": db_status,
            "frontend": os.path.exists(FRONTEND_PATH)
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "unhealthy",
            "error": str(e)
        }, status_code=500)

# Информационный маршрут
@app.get("/api/info")
async def api_info():
    """Информация об API"""
    return {
        "name": "Столовая API",
        "version": "1.0.0",
        "author": "Кассир-Админ Система",
        "endpoints": {
            "cashier_api": "/api/cashier",
            "admin_api": "/api/admin",
            "reports_api": "/api/reports",
            "documentation": "/api/docs",
            "health_check": "/health"
        }
    }

# Обработчик 404 ошибок
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Ресурс не найден", "path": request.url.path}
    )
