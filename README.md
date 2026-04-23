# SmartWallet Backend API

Backend-сервис для SmartWallet: управление картами, транзакциями, подбор лучшей карты по категории кэшбэка и рекомендации ассистента.

## О проекте

`SmartWallet Backend` — API-слой приложения, который:
- хранит пользователей, карты и транзакции;
- рассчитывает/подбирает наиболее выгодную карту по категории трат;
- отдает рекомендации через ассистента.

Цель проекта: предоставить мобильному/веб-клиенту единый backend с авторизацией, бизнес-логикой и доступом к данным.

## Что внутри

- FastAPI-приложение с модульными роутерами
- JWT-аутентификация и доступ к защищенным endpoint-ам
- SQLAlchemy ORM + PostgreSQL
- Pydantic-схемы для валидации запросов/ответов

## Архитектура

Проект разделен по слоям:

- `main.py` - точка входа, инициализация приложения, CORS, подключение роутеров
- `config.py` - конфигурация из переменных окружения
- `database.py` - подключение к БД и сессии
- `models.py` - SQLAlchemy-модели
- `schemas.py` - Pydantic-схемы DTO
- `auth.py` - логика аутентификации, токены и защита endpoint-ов
- `routers/` - HTTP API по доменам:
  - `auth.py`
  - `cards.py`
  - `transactions.py`
  - `assistant.py`
  - `cashback.py`

## Основные endpoint-ы

- `GET /` - сервисная информация
- `GET /health` - проверка доступности сервиса
- `POST /auth/register`, `POST /auth/login`, `GET /auth/profile`
- `GET/POST /cards`, `GET /cards/{id}`
- `GET/POST /transactions`
- `GET /assistant/recommendations`, `POST /assistant/chat`
- `GET /cashback/best-card?category=...`

Интерактивная спецификация: `http://localhost:8000/docs`

## Требования

- Python 3.10+
- `pip`
- PostgreSQL 14+ (или запуск через `docker compose`)

## Запуск локально (PostgreSQL)

1. Установить зависимости:

```bash
pip install -r requirements.txt
```

2. Поднять PostgreSQL и создать БД `smartwallet` (пример для локальной БД):

```sql
CREATE DATABASE smartwallet;
```

3. Настроить `.env`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/smartwallet
SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

4. Инициализировать таблицы и тестовые данные:

```bash
python init_db.py
```

5. Запустить сервис:

```bash
python run_server.py
```

Альтернатива:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Переменные окружения

Поддерживаемые параметры (`.env`, опционально):

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/smartwallet
SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Docker

Запуск API + PostgreSQL:

```bash
docker compose up --build
```

После запуска API доступно на `http://localhost:8000`, PostgreSQL - на `localhost:5432`.

## Миграции (Alembic)

Применить миграции:

```bash
python -m alembic upgrade head
```

Создать новую миграцию после изменения моделей:

```bash
python -m alembic revision --autogenerate -m "describe_changes"
```

## Структура репозитория

```text
.
|-- main.py
|-- config.py
|-- database.py
|-- models.py
|-- schemas.py
|-- auth.py
|-- requirements.txt
|-- run_server.py
|-- init_db.py
|-- alembic.ini
|-- alembic/
|   |-- env.py
|   `-- versions/
|       `-- 0001_initial_schema.py
|-- routers/
|   |-- auth.py
|   |-- cards.py
|   |-- transactions.py
|   |-- assistant.py
|   `-- cashback.py
|-- tests/
|   |-- test_backend_happy_path.py
|   |-- test_chat.py
|   |-- test_chat_formatting.py
|   `-- test_recommendations.py
|-- tools/
|   |-- chat_client.py
|   |-- improved_recommendations_example.py
|   `-- verify_register.py
`-- README.md
```

## Примечание

- `smartwallet.db` больше не используется: проект переведен на PostgreSQL.
- Инициализация БД выполняется через миграции Alembic (`python -m alembic upgrade head`).
