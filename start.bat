@echo off
echo ============================================================
echo Система учета аудиторного фонда университета
echo ============================================================
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Ошибка: Python не найден. Установите Python 3.8+ и добавьте его в PATH.
    pause
    exit /b 1
)

REM Проверяем наличие виртуального окружения
if not exist "venv" (
    echo Создание виртуального окружения...
    python -m venv venv
    if errorlevel 1 (
        echo Ошибка при создании виртуального окружения.
        pause
        exit /b 1
    )
)

REM Активируем виртуальное окружение
echo Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Устанавливаем зависимости
echo Установка зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
    echo Ошибка при установке зависимостей.
    pause
    exit /b 1
)

REM Запускаем приложение
echo.
echo Запуск приложения...
python run.py

pause
