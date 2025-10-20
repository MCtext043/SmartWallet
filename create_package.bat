@echo off
chcp 65001 >nul
echo ========================================
echo    Создание пакета SmartWallet (SQLite)
echo ========================================
echo.

echo 📦 Создание архива SmartWallet (SQLite)...

REM Создаем папку для архива
if exist "SmartWallet_Package" rmdir /s /q "SmartWallet_Package"
mkdir "SmartWallet_Package"

REM Копируем все необходимые файлы
copy "main.py" "SmartWallet_Package\"
copy "config.py" "SmartWallet_Package\"
copy "database.py" "SmartWallet_Package\"
copy "models.py" "SmartWallet_Package\"
copy "schemas.py" "SmartWallet_Package\"
copy "auth.py" "SmartWallet_Package\"
copy "init_db.py" "SmartWallet_Package\"
copy "run_server.py" "SmartWallet_Package\"
copy "test_chat.py" "SmartWallet_Package\"
copy "chat_client.py" "SmartWallet_Package\"
copy "requirements.txt" "SmartWallet_Package\"

REM Копируем папку routers
xcopy "routers" "SmartWallet_Package\routers\" /E /I /Q

REM Копируем bat файлы
copy "ЗАПУСК.bat" "SmartWallet_Package\"
copy "INSTALL.bat" "SmartWallet_Package\"
copy "START.bat" "SmartWallet_Package\"
copy "install_python.bat" "SmartWallet_Package\"
copy "setup_firewall.bat" "SmartWallet_Package\"

REM Копируем инструкции
copy "ИНСТРУКЦИЯ.txt" "SmartWallet_Package\"
copy "КАК_ЗАПУСТИТЬ.txt" "SmartWallet_Package\"
copy "MOBILE_SETUP.md" "SmartWallet_Package\"
copy "README.md" "SmartWallet_Package\"

echo ✅ Файлы скопированы
echo.

REM Создаем ZIP архив
echo 📦 Создание ZIP архива...
powershell -command "Compress-Archive -Path 'SmartWallet_Package\*' -DestinationPath 'SmartWallet_API.zip' -Force"

if exist "SmartWallet_API.zip" (
    echo ✅ Архив создан: SmartWallet_API.zip
    echo.
    echo 📋 Содержимое архива:
    echo    - ЗАПУСК.bat (главный файл для запуска)
    echo    - ИНСТРУКЦИЯ.txt (простая инструкция)
    echo    - Все исходные файлы
    echo.
    echo 🎯 Для распространения просто отправьте файл SmartWallet_API.zip
    echo    Получатель должен:
    echo    1. Распаковать архив
    echo    2. Запустить ЗАПУСК.bat
    echo    3. Всё!
) else (
    echo ❌ Ошибка создания архива
)

REM Удаляем временную папку
rmdir /s /q "SmartWallet_Package"

echo.
echo 🎉 Готово!
pause
