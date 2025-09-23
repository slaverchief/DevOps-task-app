# PowerShell скрипт для запуска приложения учета аудиторного фонда университета

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Система учета аудиторного фонда университета" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Проверяем наличие Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Найден Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Ошибка: Python не найден. Установите Python 3.8+ и добавьте его в PATH." -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

# Проверяем наличие виртуального окружения
if (-not (Test-Path "venv")) {
    Write-Host "Создание виртуального окружения..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Ошибка при создании виртуального окружения." -ForegroundColor Red
        Read-Host "Нажмите Enter для выхода"
        exit 1
    }
}

# Активируем виртуальное окружение
Write-Host "Активация виртуального окружения..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Устанавливаем зависимости
Write-Host "Установка зависимостей..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Ошибка при установке зависимостей." -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

# Запускаем приложение
Write-Host ""
Write-Host "Запуск приложения..." -ForegroundColor Green
Write-Host "Приложение будет доступно по адресу: http://127.0.0.1:8000/" -ForegroundColor Cyan
Write-Host "Административный интерфейс: http://127.0.0.1:8000/admin/" -ForegroundColor Cyan
Write-Host "Логин: admin, Пароль: admin123" -ForegroundColor Cyan
Write-Host ""
Write-Host "Для остановки сервера нажмите Ctrl+C" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

python run.py

Read-Host "Нажмите Enter для выхода"
