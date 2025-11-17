from .settings import *  # noqa

# Тестовая БД: SQLite в памяти
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}


