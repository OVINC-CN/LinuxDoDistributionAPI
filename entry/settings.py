import os
from pathlib import Path

import pymysql
from environ import environ
from ovinc_client.core.logger import get_logging_config_dict
from ovinc_client.core.utils import getenv_or_raise, strtobool

pymysql.install_as_MySQLdb()

# Base Dir
BASE_DIR = Path(__file__).resolve().parent.parent

# Env
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# DEBUG
DEBUG = strtobool(os.getenv("DEBUG", "False"))

# APP_CODE & SECRET
APP_CODE = getenv_or_raise("APP_CODE")
APP_SECRET = getenv_or_raise("APP_SECRET")
SECRET_KEY = getenv_or_raise("APP_SECRET")

# Hosts
BACKEND_URL = getenv_or_raise("BACKEND_URL")
ALLOWED_HOSTS = getenv_or_raise("ALLOWED_HOSTS").split(",")
CORS_ALLOW_CREDENTIALS = strtobool(os.getenv("CORS_ALLOW_CREDENTIALS", "True"))
CORS_ORIGIN_WHITELIST = getenv_or_raise("CORS_ORIGIN_WHITELIST").split(",")
CSRF_TRUSTED_ORIGINS = CORS_ORIGIN_WHITELIST
FRONTEND_URL = getenv_or_raise("FRONTEND_URL")

# APPs
INSTALLED_APPS = [
    "daphne",
    "simpleui",
    "corsheaders",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "sslserver",
    "ovinc_client.account",
    "ovinc_client.trace",
    "apps.cel",
    "apps.home",
    "apps.oauth",
    "apps.vcd",
    "apps.tcaptcha",
]

# MIDDLEWARE
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "ovinc_client.core.middlewares.CSRFExemptMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "ovinc_client.core.middlewares.SQLDebugMiddleware",
]
if not DEBUG:
    MIDDLEWARE += ["ovinc_client.core.middlewares.UnHandleExceptionMiddleware"]

# Urls
ROOT_URLCONF = "entry.urls"

# TEMPLATES
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

# DB and Cache
DATABASES = {
    "default": {
        "ENGINE": "dj_db_conn_pool.backends.mysql",
        "NAME": getenv_or_raise("DB_NAME"),
        "USER": getenv_or_raise("DB_USER"),
        "PASSWORD": getenv_or_raise("DB_PASSWORD"),
        "HOST": getenv_or_raise("DB_HOST"),
        "PORT": int(getenv_or_raise("DB_PORT")),
        "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", str(60 * 60))),
        "OPTIONS": {"charset": "utf8mb4"},
        "POOL_OPTIONS": {
            "POOL_SIZE": int(os.getenv("DB_POOL_SIZE", "200")),
            "MAX_OVERFLOW": int(os.getenv("DB_POOL_MAX_OVERFLOW", "800")),
        },
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
REDIS_HOST = getenv_or_raise("REDIS_HOST")
REDIS_PORT = int(getenv_or_raise("REDIS_PORT"))
REDIS_USER = os.getenv("REDIS_USER", "")
REDIS_PASSWORD = getenv_or_raise("REDIS_PASSWORD")
REDIS_DB = int(getenv_or_raise("REDIS_DB"))
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_USER}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
    }
}

# ASGI
ASGI_APPLICATION = "entry.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                f"redis://{REDIS_USER}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
            ],
        },
    },
}

# Auth
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# International
LANGUAGE_CODE = os.getenv("DEFAULT_LANGUAGE", "zh-hans")
TIME_ZONE = os.getenv("DEFAULT_TIME_ZONE", "Asia/Shanghai")
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGES = (("zh-hans", "中文简体"), ("en", "English"))
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

# Static
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "staticfiles")]

# Session
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", f"{'dev-' if DEBUG else ''}{APP_CODE}-sessionid")
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = int(os.getenv("SESSION_COOKIE_AGE", str(60 * 60 * 24)))
SESSION_COOKIE_DOMAIN = os.getenv("SESSION_COOKIE_DOMAIN")

# Log
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")
LOGGING = get_logging_config_dict(log_level=LOG_LEVEL, log_format=LOG_FORMAT)

# rest_framework
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["ovinc_client.core.renderers.APIRenderer"],
    "DEFAULT_PAGINATION_CLASS": "ovinc_client.core.paginations.NumPagination",
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
    "DEFAULT_THROTTLE_RATES": {"receive_virtual_content": "1/s"},
    "EXCEPTION_HANDLER": "ovinc_client.core.exceptions.exception_handler",
    "UNAUTHENTICATED_USER": "ovinc_client.account.models.CustomAnonymousUser",
    "DEFAULT_AUTHENTICATION_CLASSES": ["ovinc_client.core.auth.LoginRequiredAuthenticate"],
}

# User
AUTH_USER_MODEL = "account.User"

# Celery
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_ACCEPT_CONTENT = ["pickle", "json"]
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
BROKER_URL = f"redis://{REDIS_USER}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# APM
ENABLE_TRACE = strtobool(os.getenv("ENABLE_TRACE", "False"))
SERVICE_NAME = os.getenv("SERVICE_NAME", APP_CODE)
OTLP_HOST = os.getenv("OTLP_HOST", "http://127.0.0.1:4317")
OTLP_TOKEN = os.getenv("OTLP_TOKEN", "")

# RUM
RUM_ID = os.getenv("RUM_ID", "")
RUM_HOST = os.getenv("RUM_HOST", "https://rumt-zh.com")

# OVINC
OVINC_API_DOMAIN = getenv_or_raise("OVINC_API_DOMAIN")
OVINC_WEB_URL = getenv_or_raise("OVINC_WEB_URL")

# Tencent Cloud
QCLOUD_SECRET_ID = os.getenv("QCLOUD_SECRET_ID", "")
QCLOUD_SECRET_KEY = os.getenv("QCLOUD_SECRET_KEY", "")

# Captcha
CAPTCHA_TCLOUD_ID = os.getenv("CAPTCHA_TCLOUD_ID", QCLOUD_SECRET_ID)
CAPTCHA_TCLOUD_KEY = os.getenv("CAPTCHA_TCLOUD_KEY", QCLOUD_SECRET_KEY)
CAPTCHA_ENABLED = strtobool(os.getenv("CAPTCHA_ENABLED", "False"))
CAPTCHA_APP_ID = int(os.getenv("CAPTCHA_APP_ID", "0"))
CAPTCHA_APP_SECRET = os.getenv("CAPTCHA_APP_SECRET", "")
CAPTCHA_APP_INFO_TIMEOUT = int(os.getenv("CAPTCHA_APP_INFO_TIMEOUT", "600"))
CAPTCHA_PASS_THROUGH_SECONDS = int(os.getenv("CAPTCHA_PASS_THROUGH_SECONDS", "0"))
CAPTCHA_BLACKLIST_CHECK_SECONDS = int(os.getenv("CAPTCHA_BLACKLIST_CHECK_SECONDS", str(60 * 60 * 24)))
CAPTCHA_BLACKLIST_COUNT = int(os.getenv("CAPTCHA_BLACKLIST_COUNT", "3"))
CAPTCHA_BLACKLIST_CACHE_TIMEOUT = int(os.getenv("CAPTCHA_BLACKLIST_CACHE_TIMEOUT", str(60 * 10)))

# OAuth
OAUTH_SSL_VERIFY = strtobool(os.getenv("OAUTH_SSL_VERIFY", "True"))
OAUTH_PROXY_URL = os.getenv("OAUTH_PROXY_URL") or None
OAUTH_STATE_TIMEOUT = int(os.getenv("OAUTH_STATE_TIMEOUT") or 60 * 10)
OAUTH2_CLIENT = {
    "provider": {
        "client_id": getenv_or_raise("OAUTH2_CLIENT_ID"),
        "client_secret": getenv_or_raise("OAUTH2_CLIENT_SECRET"),
        "authorize_url": getenv_or_raise("OAUTH2_AUTHORIZE_URL"),
        "access_token_url": getenv_or_raise("OAUTH2_TOKEN_URL"),
        "userinfo_url": getenv_or_raise("OAUTH2_USERINFO_URL"),
    }
}
