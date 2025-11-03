#!/usr/bin/env python
"""
Скрипт для быстрого запуска приложения учета аудиторного фонда университета
"""

import os
import sys
import subprocess

def main():
    print("=" * 60)
    print("Система учета аудиторного фонда университета")
    print("=" * 60)
    
    # Проверяем, что мы в правильной директории
    if not os.path.exists('manage.py'):
        print("Ошибка: manage.py не найден. Запустите скрипт из корневой директории проекта.")
        sys.exit(1)
    
    # Проверяем наличие базы данных
    if not os.path.exists('db.sqlite3'):
        print("База данных не найдена. Выполняем инициализацию...")
        try:
            subprocess.run([sys.executable, 'init_db.py'], check=True)
            print("База данных успешно инициализирована!")
        except subprocess.CalledProcessError:
            print("Ошибка при инициализации базы данных.")
            sys.exit(1)
    
    print("\nЗапуск сервера разработки...")
    print("Приложение будет доступно по адресу: http://127.0.0.1:8000/")
    print("Административный интерфейс: http://127.0.0.1:8000/admin/")
    print("Логин: admin, Пароль: admin123")
    print("\nДля остановки сервера нажмите Ctrl+C")
    print("=" * 60)
    
    try:
        subprocess.run([sys.executable, 'manage.py', 'runserver'], check=True)
    except KeyboardInterrupt:
        print("\n\nСервер остановлен.")
    except subprocess.CalledProcessError as e:
        print(f"\nОшибка при запуске сервера: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
