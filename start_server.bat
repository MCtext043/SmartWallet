@echo off
echo ========================================
echo    SmartWallet API Server
echo ========================================
echo.

REM Проверяем, установлен ли Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден! Установите Python с https://python.org
    pause
    exit /b 1
)

REM Проверяем, установлены ли зависимости
echo 🔍 Проверка зависимостей...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo 📦 Установка зависимостей...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Ошибка установки зависимостей
        pause
        exit /b 1
    )
)

REM Инициализируем базу данных
echo 🗄️  Инициализация базы данных...
python init_db.py
if errorlevel 1 (
    echo ❌ Ошибка инициализации базы данных
    pause
    exit /b 1
)

REM Запускаем сервер
echo 🚀 Запуск сервера...
python run_server.py

pause
