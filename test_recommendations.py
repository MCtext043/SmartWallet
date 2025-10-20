"""
Тестовый скрипт для проверки персонализированных рекомендаций
"""
import requests
import json

def test_recommendations_api():
    base_url = "http://localhost:8000"
    
    print("🎯 Тест персонализированных рекомендаций SmartWallet")
    print("=" * 60)
    
    # Тестовые данные
    phone = "+79001234567"
    password = "password123"
    
    # 1. Авторизация
    print("1. Авторизация...")
    login_response = requests.post(
        f"{base_url}/auth/login",
        json={"phone": phone, "password": password}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Ошибка авторизации: {login_response.status_code}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Авторизация успешна")
    
    # 2. Получение рекомендаций
    print("\n2. Получение персонализированных рекомендаций...")
    
    recommendations_response = requests.get(
        f"{base_url}/assistant/recommendations",
        headers=headers
    )
    
    if recommendations_response.status_code == 200:
        recommendations = recommendations_response.json()
        print(f"✅ Получено {len(recommendations)} рекомендаций:")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n📋 Рекомендация {i}:")
            print(f"   Тип: {rec['type']}")
            print(f"   Сообщение: {rec['message']}")
            print(f"   Дата: {rec['created_at']}")
    else:
        print(f"❌ Ошибка: {recommendations_response.status_code} - {recommendations_response.text}")
    
    # 3. Тест с новыми транзакциями
    print("\n3. Создание тестовых транзакций для анализа...")
    
    # Получаем карты пользователя
    cards_response = requests.get(f"{base_url}/cards", headers=headers)
    if cards_response.status_code == 200:
        cards = cards_response.json()
        if cards:
            card_id = cards[0]["id"]
            
            # Создаем несколько тестовых транзакций
            test_transactions = [
                {"card_id": card_id, "amount": 2000.0, "category": "еда"},
                {"card_id": card_id, "amount": 1500.0, "category": "транспорт"},
                {"card_id": card_id, "amount": 3000.0, "category": "еда"},
            ]
            
            for trans in test_transactions:
                trans_response = requests.post(
                    f"{base_url}/transactions",
                    headers=headers,
                    json=trans
                )
                if trans_response.status_code == 200:
                    print(f"✅ Создана транзакция: {trans['category']} - {trans['amount']}₽")
                else:
                    print(f"❌ Ошибка создания транзакции: {trans_response.status_code}")
    
    # 4. Получение обновленных рекомендаций
    print("\n4. Получение обновленных рекомендаций после транзакций...")
    
    # Очищаем старые рекомендации (имитируем новый день)
    print("   (В реальном приложении рекомендации обновляются автоматически)")
    
    recommendations_response = requests.get(
        f"{base_url}/assistant/recommendations",
        headers=headers
    )
    
    if recommendations_response.status_code == 200:
        recommendations = recommendations_response.json()
        print(f"✅ Получено {len(recommendations)} рекомендаций:")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n📋 Рекомендация {i}:")
            print(f"   Тип: {rec['type']}")
            print(f"   Сообщение: {rec['message']}")
    else:
        print(f"❌ Ошибка: {recommendations_response.status_code}")
    
    print("\n🎉 Тестирование завершено!")

if __name__ == "__main__":
    try:
        test_recommendations_api()
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу")
        print("Убедитесь, что сервер запущен на http://localhost:8000")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
