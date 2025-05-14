from pathlib import Path
from decouple import config, Csv
import os
from datetime import timedelta
from dotenv import load_dotenv
import platform

load_dotenv()

DJANGO_ENV = config('DJANGO_ENV', default='production')

# Hack : Other's system for configuration
# BASE_OS = platform.system()  # 'Windows', 'Linux', 'Darwin'

# BASE DIRECTORY
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET KEY & DEBUG MODE
SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config("DJANGO_DEBUG", default=(DJANGO_ENV == "development"), cast=bool)

# ALLOWED HOSTS
ALLOWED_HOSTS = [
    'facebook-poster-backend.ezbitly.com',
    'www.facebook-poster-backend.ezbitly.com',
    '127.0.0.1',
    'localhost',
    'facebook-poster-backend.onrender.com',
]

# INSTALLED APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'facebook_poster',
    'rest_framework',
    'rest_framework_simplejwt',
    'social_django', 
    # 'django_celery_beat',
]

# MIDDLEWARE
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS SETTINGS
CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://facebook-poster.ezbitly.com"
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'content-type',
    'authorization',
    'x-csrftoken',
]

# URL CONFIGURATION
ROOT_URLCONF = 'backend.urls'
WSGI_APPLICATION = 'backend.wsgi.application'

# DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'facebook_poster/static')]

# Media is common for both
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# AUTHENTICATION & PASSWORD VALIDATION
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# INTERNATIONALIZATION
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# CACHING CONFIGURATION
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': BASE_DIR / 'cache',
    }
}

# hack: Celery configuration for deleting file (No use)
# # CELERY CONFIGURATION
# CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
# CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_TIMEZONE = 'Asia/Dhaka'
# # settings.py or celery.py file
# CELERY_WORKER_POOL_RESTARTS = True  # Restart workers automatically if they fail
# CELERY_TASK_ACKS_LATE = True        # Acknowledge tasks late to avoid losing them on crash

# REST FRAMEWORK & JWT AUTHENTICATION
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=45),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# todo: Set PayPal environment mode
if DJANGO_ENV == "development":
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'facebook_poster/static')]
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_dev')  # Added for development

    FRONTEND_URL = "http://localhost:3000"

    FACEBOOK_REDIRECT_URI = "http://127.0.0.1:8000/api/facebook/callback/"
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

    FRONTEND_URL = "https://facebook-poster.ezbitly.com"   

    FACEBOOK_REDIRECT_URI = "https://facebook-poster-backend.onrender.com/api/facebook/callback/" 

# SOCIAL AUTHENTICATION
AUTHENTICATION_BACKENDS = (
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# todo: Forgot Password Email Settings (SMTP)
# EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
# EMAIL_HOST = os.getenv('EMAIL_HOST')
# EMAIL_PORT = os.getenv('EMAIL_PORT')
# EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
# DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

# note: Cache time out 
CACHE_TIMEOUT = 45 * 60  # 45 minutes for cache time out

# hack: Automatic file delete timer (No use)
# DELETE_GENERATED_AUDIO_DELAY_SECONDS = 10 * 60 # 10 minutes for production
# DELETE_CONVERTED_AUDIO_DELAY_SECONDS = 10 * 60 # 10 minutes for production


