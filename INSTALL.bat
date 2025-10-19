@echo off
chcp 65001 >nul
echo ========================================
echo    SmartWallet API - Установщик
echo ========================================
echo.

REM Проверяем права администратора
net session >nul 2>&1
if errorlevel 1 (
    echo ❌ Требуются права администратора!
    echo Правый клик на файле → "Запуск от имени администратора"
    pause
    exit /b 1
)

echo 🔍 Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo.
    echo 📥 Скачивание Python...
    echo Откройте https://python.org/downloads/
    echo Скачайте и установите Python 3.8+
    echo Обязательно отметьте "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo ✅ Python найден
echo.

echo 📦 Установка зависимостей...
pip install fastapi uvicorn sqlalchemy python-jose[cryptography] passlib[bcrypt] python-multipart pydantic pydantic-settings python-dotenv
if errorlevel 1 (
    echo ❌ Ошибка установки зависимостей
    pause
    exit /b 1
)

echo ✅ Зависимости установлены
echo.

echo 🗄️ Инициализация базы данных...
python init_db.py
if errorlevel 1 (
    echo ❌ Ошибка инициализации базы данных
    pause
    exit /b 1
)

echo ✅ База данных создана
echo.

echo 🔥 Настройка брандмауэра...
netsh advfirewall firewall add rule name="SmartWallet API" dir=in action=allow protocol=TCP localport=8000 >nul 2>&1
echo ✅ Брандмауэр настроен
echo.

echo 🎉 Установка завершена!
echo.
echo ========================================
echo    Готово к запуску!
echo ========================================
echo.
echo 📱 Для запуска используйте:
echo    1. Дважды кликните на START.bat
echo    2. Или запустите run_server.py в PyCharm
echo.
echo 🌐 После запуска API будет доступен по адресу:
echo    http://localhost:8000
echo    http://[ВАШ_IP]:8000
echo.
echo 📖 Документация: http://[ВАШ_IP]:8000/docs
echo.
echo 🔑 Тестовые данные:
echo    Телефон: +79001234567
echo    Пароль: password123
echo.
pause
