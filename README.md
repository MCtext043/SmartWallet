# 🚀 SmartWallet Backend API

Backend для приложения SmartWallet - автоматический поиск карты с лучшим кэшбэком для оплаты.

## ⚡ БЫСТРЫЙ ЗАПУСК (для пользователей)

1. **Скачайте архив** `SmartWallet_API.zip`
2. **Распакуйте** в любую папку
3. **Запустите** `ЗАПУСК.bat`
4. **Готово!** API работает на http://localhost:8000

📖 **Подробная инструкция**: `ИНСТРУКЦИЯ.txt`

## Технологии

- **FastAPI** - современный веб-фреймворк для создания API
- **PostgreSQL** - реляционная база данных
- **SQLAlchemy** - ORM для работы с базой данных
- **Alembic** - миграции базы данных
- **JWT** - аутентификация
- **Pydantic** - валидация данных

## Установка и запуск

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка базы данных

1. Установите PostgreSQL
2. Создайте базу данных:
```sql
CREATE DATABASE smartwallet;
```

3. Создайте файл `.env` в корне проекта:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/smartwallet
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Запуск приложения

#### Вариант 1: Через PyCharm
1. Откройте файл `run_server.py`
2. Нажмите **Ctrl+Shift+F10** (Run 'run_server')
3. Или правый клик на файле → **Run 'run_server'**

#### Вариант 2: Через командную строку
```bash
python run_server.py
```

#### Вариант 3: Через bat файл (Windows)
Дважды кликните на `start_server.bat`

#### Вариант 4: Стандартный способ
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Доступ к API

После запуска сервер будет доступен по адресам:
- **Локально**: http://localhost:8000
- **В сети**: http://[ВАШ_IP]:8000 (IP будет показан в консоли)
- **Документация**: http://[ВАШ_IP]:8000/docs

### 5. Доступ с других устройств

1. **Узнайте IP адрес** вашего компьютера (показан в консоли при запуске)
2. **Убедитесь, что порт 8000 открыт** в брандмауэре Windows
3. **Подключитесь с другого устройства** по адресу: `http://[IP]:8000`

#### Настройка брандмауэра Windows:
1. Откройте **Панель управления** → **Система и безопасность** → **Брандмауэр Windows**
2. Нажмите **"Разрешить взаимодействие с приложением"**
3. Найдите **Python** и разрешите для **частной и общедоступной сети**
4. Или добавьте правило для порта **8000**

## API Endpoints

### Аутентификация
- `POST /auth/register` - Регистрация пользователя
- `POST /auth/login` - Вход в систему
- `GET /auth/profile` - Получить профиль пользователя

### Карты
- `GET /cards` - Список карт пользователя
- `POST /cards` - Добавить карту
- `GET /cards/{id}` - Детали карты

### Транзакции
- `GET /transactions` - История транзакций
- `POST /transactions` - Создать транзакцию

### Ассистент
- `GET /assistant/recommendations` - Получить рекомендации

### Кэшбэк
- `GET /cashback/best-card?category=еда` - Найти лучшую карту для категории

## Структура базы данных

### Таблица users
- `id` - ID пользователя
- `phone` - Телефон
- `email` - Email
- `name` - Имя
- `password_hash` - Хэш пароля
- `created_at` - Дата регистрации

### Таблица cards
- `id` - ID карты
- `user_id` - Владелец карты
- `bank_name` - Название банка
- `card_name` - Название карты
- `last4` - Последние 4 цифры
- `cashback_rules` - Правила кэшбэка (JSON)
- `limit_monthly` - Месячный лимит кэшбэка
- `created_at` - Дата добавления

### Таблица transactions
- `id` - ID транзакции
- `user_id` - Пользователь
- `card_id` - Карта
- `amount` - Сумма
- `category` - Категория
- `cashback_earned` - Заработанный кэшбэк
- `created_at` - Дата транзакции

### Таблица recommendations
- `id` - ID рекомендации
- `user_id` - Пользователь
- `message` - Текст рекомендации
- `type` - Тип ("совет" / "акция")
- `created_at` - Дата создания

## Примеры использования

### Регистрация пользователя
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+79001234567",
    "email": "user@example.com",
    "name": "Иван Иванов",
    "password": "password123"
  }'
```

### Добавление карты
```bash
curl -X POST "http://localhost:8000/cards" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bank_name": "Сбербанк",
    "card_name": "Сбербанк Премьер",
    "last4": "1234",
    "cashback_rules": {"еда": 5, "транспорт": 3, "прочее": 1},
    "limit_monthly": 5000.00
  }'
```

### Создание транзакции
```bash
curl -X POST "http://localhost:8000/transactions" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "card_id": 1,
    "amount": 1000.00,
    "category": "еда"
  }'
```

### Поиск лучшей карты для категории
```bash
curl -X GET "http://localhost:8000/cashback/best-card?category=еда" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Разработка

### Структура проекта
```
├── main.py                 # Главный файл приложения
├── config.py              # Конфигурация
├── database.py            # Настройка базы данных
├── models.py              # SQLAlchemy модели
├── schemas.py             # Pydantic схемы
├── auth.py                # Аутентификация
├── routers/               # API роутеры
│   ├── auth.py           # Аутентификация
│   ├── cards.py          # Карты
│   ├── transactions.py   # Транзакции
│   ├── assistant.py      # Рекомендации
│   └── cashback.py       # Кэшбэк
├── requirements.txt       # Зависимости
└── README.md             # Документация
```

### Миграции базы данных

Для создания миграции:
```bash
alembic revision --autogenerate -m "Описание изменений"
```

Для применения миграций:
```bash
alembic upgrade head
```
