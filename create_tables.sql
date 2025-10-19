-- Создание базы данных (если еще не создана)
-- CREATE DATABASE smartwallet;

-- Подключение к базе данных smartwallet
-- \c smartwallet;

-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    phone VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    password_hash VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание таблицы карт
CREATE TABLE IF NOT EXISTS cards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    bank_name VARCHAR NOT NULL,
    card_name VARCHAR NOT NULL,
    last4 VARCHAR(4) NOT NULL,
    cashback_rules JSONB,
    limit_monthly DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание таблицы транзакций
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    card_id INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    category VARCHAR NOT NULL,
    cashback_earned DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание таблицы рекомендаций
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    type VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание индексов для оптимизации
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_cards_user_id ON cards(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_card_id ON transactions(card_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON recommendations(user_id);

-- Вставка тестовых данных
INSERT INTO users (phone, email, name, password_hash) VALUES 
('+79001234567', 'test@example.com', 'Тестовый Пользователь', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/4QjKq2a')
ON CONFLICT (phone) DO NOTHING;

-- Получаем ID пользователя для тестовых данных
DO $$
DECLARE
    user_id_var INTEGER;
BEGIN
    SELECT id INTO user_id_var FROM users WHERE phone = '+79001234567';
    
    -- Вставляем тестовые карты
    INSERT INTO cards (user_id, bank_name, card_name, last4, cashback_rules, limit_monthly) VALUES 
    (user_id_var, 'Сбербанк', 'Сбербанк Премьер', '1234', '{"еда": 5, "транспорт": 3, "прочее": 1}', 5000.00),
    (user_id_var, 'Тинькофф', 'Тинькофф Платинум', '5678', '{"еда": 3, "транспорт": 5, "прочее": 2}', 3000.00),
    (user_id_var, 'Альфа-Банк', 'Альфа-Банк 100 дней', '9012', '{"еда": 2, "транспорт": 2, "прочее": 5}', 10000.00)
    ON CONFLICT DO NOTHING;
    
    -- Вставляем тестовые транзакции
    INSERT INTO transactions (user_id, card_id, amount, category, cashback_earned) VALUES 
    (user_id_var, (SELECT id FROM cards WHERE last4 = '1234' LIMIT 1), 1000.00, 'еда', 50.00),
    (user_id_var, (SELECT id FROM cards WHERE last4 = '5678' LIMIT 1), 500.00, 'транспорт', 25.00),
    (user_id_var, (SELECT id FROM cards WHERE last4 = '9012' LIMIT 1), 2000.00, 'прочее', 100.00)
    ON CONFLICT DO NOTHING;
    
    -- Вставляем тестовые рекомендации
    INSERT INTO recommendations (user_id, message, type) VALUES 
    (user_id_var, 'Добавьте карты с высоким кэшбэком для разных категорий трат', 'совет'),
    (user_id_var, 'Используйте карту с максимальным кэшбэком для каждой покупки', 'совет'),
    (user_id_var, 'Проверяйте лимиты кэшбэка перед крупными покупками', 'совет')
    ON CONFLICT DO NOTHING;
END $$;
