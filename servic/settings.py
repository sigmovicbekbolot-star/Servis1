import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _

# 1. НЕГИЗГИ ЖОЛДОР
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. КООПСУЗДУК
SECRET_KEY = 'django-insecure-6!n5z08-ouw9u47_%k_01&^d^7=4_y4gxo(vcnqx8cl1v*c7ul'
DEBUG = True
ALLOWED_HOSTS = ['*']

# 3. ТИРКЕМЕЛЕР (APPS)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Сенин колдонмолоруң жана кошумчалар
    'config',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
]

# 4. ОРТОНКУ КАТМАРЛАР (MIDDLEWARE)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', # Сөзсүз 1-орундарда
    'django.middleware.locale.LocaleMiddleware',           # ТИЛ ҮЧҮН УШУЛ ЖЕРДЕ БОЛУШУ ШАРТ!
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'servic.urls'

# 5. ШАБЛОНДОР (TEMPLATES)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n', # Тилдер үчүн кошумча
            ],
        },
    },
]

WSGI_APPLICATION = 'servic.wsgi.application'

# 6. БАЗА (DATABASE)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 7. КОЛДОНУУЧУНУН МОДЕЛИ
AUTH_USER_MODEL = 'config.User'

# 8. ПАРОЛЬ ВАЛИДАЦИЯСЫ
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# 9. ТИЛ ЖАНА УБАКЫТ (I18N)
LANGUAGE_CODE = 'ky'
TIME_ZONE = 'Asia/Bishkek'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('ky', _('Kyrgyz')),
    ('ru', _('Russian')),
    ('en', _('English')),
]

# Тил файлдары сактала турган жер (Эгер котормо жасайм десең)
LOCALE_PATHS = [
    BASE_DIR / 'locale/',
]

# 10. СТАТИКА ЖАНА МЕДИА
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 11. DJANGO REST FRAMEWORK ЖӨНДӨӨЛӨРҮ
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# 12. SWAGGER (SPECTACULAR)
SPECTACULAR_SETTINGS = {
    'TITLE': 'Service.kg API',
    'DESCRIPTION': 'Сервис порталынын API документтери',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# 13. БАГЫТТОО (LOGIN/LOGOUT)
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'