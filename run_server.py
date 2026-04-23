"""
SmartWallet API Server
Простой запуск сервера для работы в сети
База данных: PostgreSQL
"""
import uvicorn
import socket
import sys

def get_ip():
    """Получает IP адрес компьютера"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "127.0.0.1"

if __name__ == "__main__":
    ip = get_ip()
    
    print("🚀 SmartWallet API запущен!")
    print(f"📱 Локально: http://localhost:8000")
    print(f"🌐 В сети: http://{ip}:8000")
    print(f"📖 Документация: http://{ip}:8000/docs")
    print("💡 Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    try:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        input("Нажмите Enter для выхода...")
