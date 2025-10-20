"""
Тестовый скрипт для проверки чата с ассистентом
"""
import requests
import json

def test_chat_api():
    base_url = "http://localhost:8000"
    
    print("🤖 Тест чата с AI ассистентом SmartWallet")
    print("=" * 50)
    
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
    
    # 2. Тест чата
    print("\n2. Тест чата с ассистентом...")
    
    test_messages = [
        "Привет, подскажи лучший кэшбэк на еду?",
        "Какая карта лучше для транспорта?",
        "Сколько кэшбэка я получу за покупку на 1000 рублей в категории еда?",
        "Дай совет по оптимизации кэшбэка"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Тест {i}: {message}")
        
        chat_response = requests.post(
            f"{base_url}/assistant/chat",
            headers=headers,
            json={"message": message}
        )
        
        if chat_response.status_code == 200:
            reply = chat_response.json()["reply"]
            print(f"🤖 Ассистент: {reply}")
        else:
            print(f"❌ Ошибка: {chat_response.status_code} - {chat_response.text}")
    
    print("\n🎉 Тестирование завершено!")

if __name__ == "__main__":
    try:
        test_chat_api()
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу")
        print("Убедитесь, что сервер запущен на http://localhost:8000")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
