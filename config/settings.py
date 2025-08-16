# Импортируем библиотеку для загрузки переменных окружения из файла .env
from dotenv import load_dotenv
import os
from pathlib import Path

# Загружаем переменные окружения из файла .env
# override=True - перезаписываем существующие переменные
load_dotenv(override=True)

# BASE_DIR - базовый путь к проекту Django
# Path(__file__) - путь к текущему файлу (settings.py)
# .resolve().parent.parent - поднимаемся на два уровня вверх (config -> pythonProject)
BASE_DIR = Path(__file__).resolve().parent.parent


# ==================== БАЗОВЫЕ НАСТРОЙКИ БЕЗОПАСНОСТИ ====================

# SECRET_KEY - секретный ключ для шифрования сессий, токенов и т.д.
# В продакшене должен быть скрыт и уникален для каждого проекта
SECRET_KEY = os.getenv("SECRET_KEY")

# DEBUG - режим отладки
# True - показывает детальные ошибки (только для разработки!)
# False - скрывает ошибки (для продакшена)
DEBUG = True

# ALLOWED_HOSTS - список разрешенных доменов для работы Django
# Пустой список [] - разрешены только localhost и 127.0.0.1
ALLOWED_HOSTS = []


# ==================== НАСТРОЙКИ ПРИЛОЖЕНИЙ ====================

# INSTALLED_APPS - список всех приложений Django
INSTALLED_APPS = [
    # Встроенные приложения Django
    'django.contrib.admin',        # Админ-панель Django
    'django.contrib.auth',         # Система аутентификации
    'django.contrib.contenttypes', # Система типов контента
    'django.contrib.sessions',     # Система сессий
    'django.contrib.messages',     # Система сообщений
    'django.contrib.staticfiles',  # Обработка статических файлов (CSS, JS, изображения)
    
    # Наши кастомные приложения
    'user',                        # Приложение для пользователей
    'booking',                     # Приложение для бронирования
    
    # Сторонние приложения
    'rest_framework'               # Django REST Framework для создания API
]

# MIDDLEWARE - промежуточное ПО (middleware)
# Это функции, которые выполняются для каждого запроса
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',           # Безопасность
    'django.contrib.sessions.middleware.SessionMiddleware',    # Управление сессиями
    'django.middleware.common.CommonMiddleware',               # Общие функции
    'django.middleware.csrf.CsrfViewMiddleware',               # Защита от CSRF атак
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Аутентификация
    'django.contrib.messages.middleware.MessageMiddleware',    # Сообщения
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Защита от clickjacking
]

# ROOT_URLCONF - главный файл с URL маршрутами
ROOT_URLCONF = 'config.urls'

# ==================== НАСТРОЙКИ ШАБЛОНОВ ====================

# TEMPLATES - настройки для HTML шаблонов
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',  # Движок шаблонов Django
        'DIRS': [BASE_DIR / 'templates'],  # Папка с шаблонами (относительно BASE_DIR)
        'APP_DIRS': True,                  # Искать шаблоны в папках приложений
        'OPTIONS': {
            'context_processors': [
                # Процессоры контекста - добавляют переменные во все шаблоны
                'django.template.context_processors.request',      # Объект request
                'django.contrib.auth.context_processors.auth',     # Информация о пользователе
                'django.contrib.auth.messages.context_processors.messages',  # Сообщения
            ],
        },
    },
]

# WSGI_APPLICATION - WSGI приложение для развертывания
WSGI_APPLICATION = 'config.wsgi.application'




#Для PostgreSQL (более мощная БД для продакшена):
DATABASES = {
     "default": {
         "ENGINE": "django.db.backends.postgresql_psycopg2",
         "NAME": os.getenv("DB_NAME"),
         "USER": os.getenv("DB_USER"),
         "PASSWORD": os.getenv("DB_PASSWORD"),
         "HOST": os.getenv("DB_HOST"),
         "PORT": os.getenv("DB_PORT"),
     }
 }


# ==================== ВАЛИДАЦИЯ ПАРОЛЕЙ ====================

# AUTH_PASSWORD_VALIDATORS - правила проверки паролей
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        # Проверяет, что пароль не похож на имя пользователя
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        # Проверяет минимальную длину пароля
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        # Проверяет, что пароль не в списке популярных паролей
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        # Проверяет, что пароль не состоит только из цифр
    },
]


# ==================== МЕЖДУНАРОДИЗАЦИЯ ====================

# LANGUAGE_CODE - язык по умолчанию
LANGUAGE_CODE = 'en-us'  # Английский (США)

# TIME_ZONE - часовой пояс
TIME_ZONE = 'UTC'  # Всемирное координированное время

# USE_I18N - включить интернационализацию (переводы)
USE_I18N = True

# USE_TZ - использовать часовые пояса
USE_TZ = True


# ==================== СТАТИЧЕСКИЕ ФАЙЛЫ ====================

# STATIC_URL - URL для статических файлов (CSS, JavaScript, изображения)
STATIC_URL = 'static/'

# STATICFILES_DIRS - дополнительные папки со статическими файлами
STATICFILES_DIRS = [BASE_DIR / "static"]

# MEDIA_URL - URL для загруженных пользователем файлов
MEDIA_URL = '/media/'

# MEDIA_ROOT - папка для хранения загруженных файлов
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==================== ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ ====================

# DEFAULT_AUTO_FIELD - тип поля по умолчанию для первичного ключа
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# AUTH_USER_MODEL - кастомная модель пользователя
# По умолчанию Django использует django.contrib.auth.models.User
# Здесь мы указываем нашу кастомную модель из приложения user
AUTH_USER_MODEL = 'user.CustomUser'
