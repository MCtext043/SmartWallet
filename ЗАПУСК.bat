@echo off
chcp 65001 >nul
title SmartWallet API

echo ========================================
echo    🚀 SMARTWALLET API
echo ========================================
echo.

REM Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo.
    echo 📥 Запуск установки Python...
    call install_python.bat
    exit /b 0
)

REM Проверяем зависимости
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo 📦 Установка зависимостей...
    call INSTALL.bat
    exit /b 0
)

REM Проверяем базу данных
if not exist "smartwallet.db" (
    echo 🗄️ Создание базы данных...
    python init_db.py
)

echo ✅ Все готово!
echo.
echo 🚀 Запуск сервера...
echo.

call START.bat
