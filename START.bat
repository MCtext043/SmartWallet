@echo off
chcp 65001 >nul
echo ========================================
echo    SmartWallet API - Запуск
echo ========================================
echo.

REM Получаем IP адрес
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set "ip=%%a"
    goto :found
)
:found
set "ip=%ip: =%"

echo 🚀 Запуск SmartWallet API...
echo.
echo 📱 Локальный доступ: http://localhost:8000
echo 🌐 Сетевой доступ: http://%ip%:8000
echo 📖 Документация: http://%ip%:8000/docs
echo.
echo 💡 Для остановки нажмите Ctrl+C
echo ========================================
echo.

python run_server.py

echo.
echo 👋 Сервер остановлен
pause
