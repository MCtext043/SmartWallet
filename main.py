from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine, apply_sqlite_migrations
from models import Base
from routers import auth, cards, transactions, assistant, cashback, demo

# Создаем таблицы в базе данных и подмешиваем колонки в существующий SQLite
Base.metadata.create_all(bind=engine)
apply_sqlite_migrations()

STATIC_DIR = Path(__file__).resolve().parent / "static"
(STATIC_DIR / "avatars").mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="SmartWallet API",
    description="API для приложения SmartWallet - автоматический поиск карты с лучшим кэшбэком",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(cards.router)
app.include_router(transactions.router)
app.include_router(assistant.router)
app.include_router(cashback.router)
app.include_router(demo.router)


@app.get("/")
def read_root():
    return {
        "message": "SmartWallet API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
