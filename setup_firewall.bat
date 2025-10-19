@echo off
echo ========================================
echo    Настройка брандмауэра Windows
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

echo 🔥 Настройка правил брандмауэра для SmartWallet API...
echo.

REM Добавляем правило для входящих подключений на порт 8000
echo 📥 Добавление правила для входящих подключений...
netsh advfirewall firewall add rule name="SmartWallet API - Inbound" dir=in action=allow protocol=TCP localport=8000
if errorlevel 1 (
    echo ❌ Ошибка добавления правила для входящих подключений
) else (
    echo ✅ Правило для входящих подключений добавлено
)

REM Добавляем правило для исходящих подключений на порт 8000
echo 📤 Добавление правила для исходящих подключений...
netsh advfirewall firewall add rule name="SmartWallet API - Outbound" dir=out action=allow protocol=TCP localport=8000
if errorlevel 1 (
    echo ❌ Ошибка добавления правила для исходящих подключений
) else (
    echo ✅ Правило для исходящих подключений добавлено
)

echo.
echo ✅ Настройка брандмауэра завершена!
echo.
echo 📋 Добавленные правила:
echo    - SmartWallet API - Inbound (порт 8000)
echo    - SmartWallet API - Outbound (порт 8000)
echo.
echo 💡 Теперь API будет доступен с других устройств в сети
echo.

pause
