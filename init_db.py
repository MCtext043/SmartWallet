"""
Скрипт для инициализации базы данных SQLite с тестовыми данными
SQLite не требует установки - встроена в Python!
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Card, Transaction, Recommendation
from auth import get_password_hash

def create_tables():
    """Создает все таблицы в базе данных SQLite"""
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы SQLite созданы")

def create_test_data():
    """Создает тестовые данные"""
    db = SessionLocal()
    
    try:
        # Проверяем, есть ли уже пользователи
        if db.query(User).first():
            print("✅ Тестовые данные уже существуют")
            return
        
        # Создаем тестового пользователя
        test_user = User(
            phone="+79001234567",
            email="test@example.com",
            name="Тестовый Пользователь",
            password_hash=get_password_hash("password123")
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✅ Создан пользователь: {test_user.name}")
        
        # Создаем тестовые карты
        cards_data = [
            {
                "bank_name": "Сбербанк",
                "card_name": "Сбербанк Премьер",
                "last4": "1234",
                "cashback_rules": {"еда": 5, "транспорт": 3, "прочее": 1},
                "limit_monthly": 5000.0
            },
            {
                "bank_name": "Тинькофф",
                "card_name": "Тинькофф Платинум",
                "last4": "5678",
                "cashback_rules": {"еда": 3, "транспорт": 5, "прочее": 2},
                "limit_monthly": 3000.0
            },
            {
                "bank_name": "Альфа-Банк",
                "card_name": "Альфа-Банк 100 дней",
                "last4": "9012",
                "cashback_rules": {"еда": 2, "транспорт": 2, "прочее": 5},
                "limit_monthly": 10000.0
            }
        ]
        
        for card_data in cards_data:
            card = Card(
                user_id=test_user.id,
                **card_data
            )
            db.add(card)
        
        db.commit()
        print("✅ Созданы тестовые карты")
        
        # Создаем тестовые транзакции
        transactions_data = [
            {"card_id": 1, "amount": 1000.0, "category": "еда", "cashback_earned": 50.0},
            {"card_id": 2, "amount": 500.0, "category": "транспорт", "cashback_earned": 25.0},
            {"card_id": 3, "amount": 2000.0, "category": "прочее", "cashback_earned": 100.0}
        ]
        
        for trans_data in transactions_data:
            transaction = Transaction(
                user_id=test_user.id,
                **trans_data
            )
            db.add(transaction)
        
        db.commit()
        print("✅ Созданы тестовые транзакции")
        
        # Создаем тестовые рекомендации
        recommendations_data = [
            {"message": "Добавьте карты с высоким кэшбэком для разных категорий трат", "type": "совет"},
            {"message": "Используйте карту с максимальным кэшбэком для каждой покупки", "type": "совет"},
            {"message": "Проверяйте лимиты кэшбэка перед крупными покупками", "type": "совет"}
        ]
        
        for rec_data in recommendations_data:
            recommendation = Recommendation(
                user_id=test_user.id,
                **rec_data
            )
            db.add(recommendation)
        
        db.commit()
        print("✅ Созданы тестовые рекомендации")
        
        print("\n🎉 База данных SQLite успешно инициализирована!")
        print("📱 Тестовый пользователь:")
        print("   Телефон: +79001234567")
        print("   Пароль: password123")
        print("🗄️ База данных: smartwallet.db (SQLite)")
        
    except Exception as e:
        print(f"❌ Ошибка при создании тестовых данных: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Инициализация базы данных SmartWallet (SQLite)...")
    create_tables()
    create_test_data()
