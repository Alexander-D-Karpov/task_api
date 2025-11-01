from datetime import timedelta
from pathlib import Path

import environ

ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
APPS_DIR = ROOT_DIR / "task_api"
env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=True)
if READ_DOT_ENV_FILE:
    env.read_env(str(ROOT_DIR / ".env"))

DEBUG = env.bool("DJANGO_DEBUG", False)
TIME_ZONE = "Europe/Moscow"
LANGUAGE_CODE = "ru-RU"
SITE_ID = 1
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [str(ROOT_DIR / "locale")]

DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.forms",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "drf_spectacular",
    "django_celery_beat",
]

LOCAL_APPS = [
    "task_api.users",
    "task_api.authentication",
    "task_api.tasks",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

STATIC_ROOT = str(ROOT_DIR / "staticfiles")
STATIC_URL = "/static/"
STATICFILES_DIRS = [str(APPS_DIR / "static")]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

MEDIA_ROOT = str(APPS_DIR / "media")
MEDIA_URL = "/media/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR / "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"
FIXTURE_DIRS = (str(APPS_DIR / "fixtures"),)

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

ADMIN_URL = "admin/"
ADMINS = [("""Alexandr Karpov""", "sanspie@akarpov.ru")]
MANAGERS = ADMINS

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_USER_MODEL = "users.User"

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

if USE_TZ:
    CELERY_TIMEZONE = TIME_ZONE

CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_RESULT_EXTENDED = True
CELERY_RESULT_BACKEND_ALWAYS_RETRY = True
CELERY_RESULT_BACKEND_MAX_RETRIES = 10
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_TIME_LIMIT = 5 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 60
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("JWT_ACCESS_TOKEN_LIFETIME", default=60)),
    "REFRESH_TOKEN_LIFETIME": timedelta(minutes=env.int("JWT_REFRESH_TOKEN_LIFETIME", default=1440)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Task Management API",
    "DESCRIPTION": "API для системы управления задачами",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api/",
    "SERVERS": [
        {"url": "http://127.0.0.1:8000", "description": "Development server"},
        {"url": "https://akarpov.ru", "description": "Production server"},
    ],
}

EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="mailhog")
EMAIL_PORT = env.int("EMAIL_PORT", default=1025)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@taskapi.local")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"verbose": {"format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"}},
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}
