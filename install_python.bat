@echo off
chcp 65001 >nul
echo ========================================
echo    Установка Python для SmartWallet (SQLite)
echo ========================================
echo.

echo 🔍 Проверка Python...
python --version >nul 2>&1
if not errorlevel 1 (
    echo ✅ Python уже установлен!
    python --version
    echo.
    echo Переходим к установке SmartWallet...
    call INSTALL.bat
    exit /b 0
)

echo ❌ Python не найден!
echo.
echo 📥 Автоматическая установка Python...
echo.

REM Создаем временный скрипт для скачивания Python
echo import urllib.request > download_python.py
echo import subprocess >> download_python.py
echo import os >> download_python.py
echo print("Скачивание Python...") >> download_python.py
echo url = "https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe" >> download_python.py
echo filename = "python_installer.exe" >> download_python.py
echo urllib.request.urlretrieve(url, filename) >> download_python.py
echo print("Запуск установщика...") >> download_python.py
echo subprocess.run([filename, "/quiet", "InstallAllUsers=1", "PrependPath=1"]) >> download_python.py
echo print("Установка завершена!") >> download_python.py

echo 🚀 Запуск установки Python...
python download_python.py

if errorlevel 1 (
    echo ❌ Ошибка автоматической установки
    echo.
    echo 📋 Ручная установка:
    echo 1. Откройте https://python.org/downloads/
    echo 2. Скачайте Python 3.8+
    echo 3. При установке отметьте "Add Python to PATH"
    echo 4. Перезапустите этот файл
    echo.
    pause
    exit /b 1
)

echo ✅ Python установлен!
echo.

REM Удаляем временный файл
del download_python.py >nul 2>&1

echo 🔄 Перезапуск для применения изменений...
echo.
echo После перезапуска автоматически запустится установка SmartWallet
pause

REM Перезапускаем с новой переменной PATH
call INSTALL.bat
