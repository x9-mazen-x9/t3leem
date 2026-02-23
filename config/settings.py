"""
Django settings for config project.
Production-ready configuration for MAJMA Platform
"""

from pathlib import Path
import os
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================
# Load .env
# ==============================
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass


# ==============================
# Security
# ==============================

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY is not set in environment variables.")

DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Production Security
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# ==============================
# Subscription Settings
# ==============================

COURSE_SUBSCRIPTION_DAYS = 35  # مدة اشتراك الطالب مع المدرس (35 يوم)
TEACHER_SUBSCRIPTION_DAYS = 31  # مدة اشتراك المدرس مع المنصة (31 يوم)


# ==============================
# Installed Apps
# ==============================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",

    # Local apps
    "apps.users",
    "apps.core",
    "apps.teachers",
    "apps.students",
    "apps.lessons",
    "apps.social",
    "apps.notifications",
    "apps.courses",
    "apps.progress",
    "apps.exams",
]


# ==============================
# Middleware
# ==============================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"


# ==============================
# Templates
# ==============================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ==============================
# Database
# ==============================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 60,
    }
}


# ==============================
# Custom User
# ==============================

AUTH_USER_MODEL = "users.User"


# ==============================
# Django REST
# ==============================

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,

    # 🔐 Anti-Spam Protection
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/day",
    },
}


SPECTACULAR_SETTINGS = {
    "TITLE": "MAJMA API",
    "DESCRIPTION": "Enterprise Educational Social Platform",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}


# ==============================
# JWT
# ==============================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# ==============================
# Redis Cache
# ==============================
# التعديل هنا: استخدام الذاكرة المحلية بدل Redis لتجنب خطأ الاتصال على ويندوز
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": os.getenv("REDIS_URL"),
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         },
#     }
# }


# ==============================
# Celery
# ==============================

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"


# ==============================
# Bunny Stream
# ==============================

BUNNY_STREAM_LIBRARY_ID = os.getenv("BUNNY_STREAM_LIBRARY_ID")
BUNNY_STREAM_API_KEY = os.getenv("BUNNY_STREAM_API_KEY")


# ==============================
# Static Files
# ==============================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# ==============================
# CORS
# ==============================

CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL", "False").lower() == "true"

if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173"
    ).split(",")

CORS_ALLOW_CREDENTIALS = True


# ==============================
# Internationalization
# ==============================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ==============================
# Logging
# ==============================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "errors.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}
