-- SQLite скрипт для создания таблиц SmartWallet
-- База данных: smartwallet.db

-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы карт
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bank_name TEXT NOT NULL,
    card_name TEXT NOT NULL,
    last4 TEXT NOT NULL,
    cashback_rules TEXT, -- JSON строка
    limit_monthly REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Создание таблицы транзакций
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    card_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    cashback_earned REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
);

-- Создание таблицы рекомендаций
CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    type TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Создание индексов для оптимизации
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_cards_user_id ON cards(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_card_id ON transactions(card_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON recommendations(user_id);

-- Вставка тестовых данных
INSERT OR IGNORE INTO users (phone, email, name, password_hash) VALUES 
('+79001234567', 'test@example.com', 'Тестовый Пользователь', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/4QjKq2a');

-- Получаем ID пользователя для тестовых данных
INSERT OR IGNORE INTO cards (user_id, bank_name, card_name, last4, cashback_rules, limit_monthly) VALUES 
(1, 'Сбербанк', 'Сбербанк Премьер', '1234', '{"еда": 5, "транспорт": 3, "прочее": 1}', 5000.0),
(1, 'Тинькофф', 'Тинькофф Платинум', '5678', '{"еда": 3, "транспорт": 5, "прочее": 2}', 3000.0),
(1, 'Альфа-Банк', 'Альфа-Банк 100 дней', '9012', '{"еда": 2, "транспорт": 2, "прочее": 5}', 10000.0);

INSERT OR IGNORE INTO transactions (user_id, card_id, amount, category, cashback_earned) VALUES 
(1, 1, 1000.0, 'еда', 50.0),
(1, 2, 500.0, 'транспорт', 25.0),
(1, 3, 2000.0, 'прочее', 100.0);

INSERT OR IGNORE INTO recommendations (user_id, message, type) VALUES 
(1, 'Добавьте карты с высоким кэшбэком для разных категорий трат', 'совет'),
(1, 'Используйте карту с максимальным кэшбэком для каждой покупки', 'совет'),
(1, 'Проверяйте лимиты кэшбэка перед крупными покупками', 'совет');
