# src/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_app(lifespan=None):
    """Фабрика для создания FastAPI приложения"""
    app = FastAPI(
        title="Restaurant Management API",
        description="API для управления рестораном с меню, заказами и отчетами",
        version="1.0.0",
        lifespan=lifespan
    )

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
