"""
Django settings for social_trends_backend project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-dev-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']  # '*' for development only


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'social_trends_backend.urls'

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

WSGI_APPLICATION = 'social_trends_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}

# CORS settings
# For development: Allow all origins to avoid CORS issues
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Also specify allowed origins (for production/reference)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Vite default port
    "http://127.0.0.1:5173",
]

# Allow CORS from any origin in development (since CORS_ALLOW_ALL_ORIGINS = True, this is redundant but kept for reference)

# Additional CORS headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# YouTube API Key (set in .env file)
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')

# Caching configuration
# Use Redis if available, otherwise fall back to database cache
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/1')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'CONNECTION_POOL_KWARGS': {
                'retry_on_timeout': True,
                'health_check_interval': 30
            },
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,  # Gracefully handle Redis failures
        },
        'KEY_PREFIX': 'social_trends',
        'TIMEOUT': None,  # Default timeout (use TTL in cache calls)
    }
}

# Fallback to database cache if Redis is not available
# This will automatically fall back if Redis connection fails
try:
    import redis
    r = redis.from_url(REDIS_URL, socket_connect_timeout=1)
    r.ping()
    print("✅ Redis cache enabled")
except:
    print("⚠️ Redis not available, using database cache fallback")
    CACHES['default'] = {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
        'TIMEOUT': None,
    }

# YouTube API Quota Configuration
YOUTUBE_QUOTA_LIMIT = int(os.getenv('YOUTUBE_QUOTA_LIMIT', '10000'))  # Daily quota limit
YOUTUBE_QUOTA_WARNING_THRESHOLD = int(os.getenv('YOUTUBE_QUOTA_WARNING_THRESHOLD', '8000'))  # Warn at 80%
YOUTUBE_QUOTA_RESET_TIME = os.getenv('YOUTUBE_QUOTA_RESET_TIME', '00:00:00')  # Pacific Time midnight

# Cache TTL Configuration (in seconds)
CACHE_TTL = {
    'channel_videos': 86400,  # 24 hours (increased to save quota)
    'video_statistics': 86400,  # 24 hours (increased to save quota)
    'channel_info': 86400,  # 24 hours - channel info rarely changes
    'trending_videos': 300,  # 5 minutes (reduced cache for trending)
    'live_videos': 60,  # 1 minute (short cache for live)
    'playlist_items': 86400,  # 24 hours (increased to save quota)
}

# Use web scraping as fallback when quota exceeded
USE_WEB_SCRAPING_FALLBACK = True

# Disable expensive Search API by default (saves 100 units per channel)
# Set to True to enable Search API, but it costs 100 quota units per channel
USE_SEARCH_API = False  # Disabled by default to save quota

# Rate Limiting Configuration
YOUTUBE_API_RATE_LIMIT = {
    'max_requests_per_second': 5,  # Conservative rate limit
    'max_requests_per_minute': 100,
}

