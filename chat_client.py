"""
Простой клиент для чата с ассистентом SmartWallet
"""
import requests
import json

class SmartWalletChatClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.headers = None
    
    def login(self, phone, password):
        """Авторизация"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"phone": phone, "password": password}
            )
            
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
                print("✅ Авторизация успешна")
                return True
            else:
                print(f"❌ Ошибка авторизации: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def chat(self, message):
        """Отправка сообщения ассистенту"""
        try:
            response = requests.post(
                f"{self.base_url}/assistant/chat",
                headers=self.headers,
                json={"message": message}
            )
            
            if response.status_code == 200:
                return response.json()["reply"]
            else:
                return f"Ошибка: {response.status_code}"
        except Exception as e:
            return f"Ошибка: {e}"
    
    def start_chat(self):
        """Интерактивный чат"""
        print("🤖 SmartWallet AI Ассистент")
        print("=" * 40)
        print("Команды: 'выход', 'exit', 'quit' - для выхода")
        print("-" * 40)
        
        while True:
            try:
                message = input("Вы: ").strip()
                
                if message.lower() in ['выход', 'exit', 'quit']:
                    print("👋 До свидания!")
                    break
                
                if not message:
                    continue
                
                print("🤖 Ассистент: ", end="", flush=True)
                reply = self.chat(message)
                print(reply)
                
            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                break

def main():
    client = SmartWalletChatClient()
    
    # Авторизация с тестовыми данными
    if not client.login("+79001234567", "password123"):
        print("Не удалось авторизоваться. Проверьте, что сервер запущен.")
        return
    
    # Запуск чата
    client.start_chat()

if __name__ == "__main__":
    main()
