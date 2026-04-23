"""
Тестовый скрипт для проверки форматирования ответов от AI ассистента
"""
import requests
import json

def test_chat_formatting():
    base_url = "http://localhost:8000"
    
    print("🎨 Тест форматирования ответов AI ассистента")
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
    
    # 2. Тест вопросов с форматированными ответами
    print("\n2. Тест форматирования ответов...")
    
    test_messages = [
        "Расскажи про мои карты?",
        "Дай рекомендации по кэшбэку",
        "Какая карта лучше для еды?",
        "Создай список моих карт с кэшбэком"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Тест {i}: {message}")
        print("-" * 40)
        
        chat_response = requests.post(
            f"{base_url}/assistant/chat",
            headers=headers,
            json={"message": message}
        )
        
        if chat_response.status_code == 200:
            reply = chat_response.json()["reply"]
            print(f"🤖 Ассистент:")
            print(reply)
            print("\n✅ Ответ отформатирован корректно")
        else:
            print(f"❌ Ошибка: {chat_response.status_code} - {chat_response.text}")
    
    # 3. Проверка JSON структуры ответа
    print("\n3. Проверка структуры JSON ответа...")
    
    test_response = requests.post(
        f"{base_url}/assistant/chat",
        headers=headers,
        json={"message": "Привет!"}
    )
    
    if test_response.status_code == 200:
        response_data = test_response.json()
        print("📋 Структура ответа:")
        print(f"   - reply: {type(response_data['reply'])}")
        print(f"   - длина: {len(response_data['reply'])} символов")
        
        # Проверяем, что нет сырого JSON в ответе
        if '{"content":' in response_data['reply']:
            print("❌ В ответе остался сырой JSON!")
        else:
            print("✅ JSON правильно обработан")
            
        # Проверяем переносы строк
        if '\\n' in response_data['reply']:
            print("❌ Переносы строк не обработаны!")
        else:
            print("✅ Переносы строк обработаны корректно")
    
    print("\n🎉 Тестирование форматирования завершено!")

if __name__ == "__main__":
    try:
        test_chat_formatting()
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу")
        print("Убедитесь, что сервер запущен на http://localhost:8000")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
