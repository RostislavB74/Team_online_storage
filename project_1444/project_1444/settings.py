import sys
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from pathlib import Path

# from django.utils.translation import gettext_lazy as _
# import os
from urllib.parse import urlparse

import environ

# from django.shortcuts import resolve_url
from django.urls import reverse_lazy

from . import __version__

# from django.utils.translation import gettext_lazy as _
# import zoneinfo
# from urllib.parse import urlparse
# from pygments.lexer import default
# import os
# from urllib.parse import urlparse
# from dotenv import load_dotenv
# from django.core.exceptions import ImproperlyConfigured

# from django.conf.global_settings import STATIC_ROOT
# import cloudinary
# import cloudinary.uploader
# import cloudinary.api
# from cloudinary.utils import cloudinary_url
# from django.conf.global_settings import LANGUAGES as GLOBAL_LANGUAGES


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR.parent / ".env")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

IS_TESTING = "test" in sys.argv
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default=None)
if not SECRET_KEY or SECRET_KEY.isspace():
    SECRET_KEY = "django-insecure-i&eu1qndfw3ooc#3@01b8)0(6z4yr(jfjh+=p1rk&@+j^o(m^i"

SITE_URL = env("SITE_URL", default="")
PROJECT_NAME = env("PROJECT_NAME", default=Path(__file__).resolve().parent.name)
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", default=False, cast=bool)
print(f"{DEBUG=}")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=None)

if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]

ALLOWED_HOSTS.append("testserver")

print(f"{ALLOWED_HOSTS=}")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_celery_beat",
    "social_django",
    "rest_framework",
    "drf_spectacular",
    "djoser",
    "rest_framework.authtoken",
    "django_extensions",
    "parler",
    "storages",  # For custom S3/Cloudinary storage class
    "cloudinary",
    "debug_toolbar",
    # "cloudinary_storage",
    "django_filters",
    # "mptt",
    # "django_countries",
    # "django_prices",
    # "django_prices_openexchangerates",
    # "django_prices_vatlayer",
    # "sorl.thumbnail",
    #
    # "django-liqpay",
    "product",
    "users.apps.UsersConfig",
    # "users",
    "cart",
    "order",
    "warehouse",
    "discounts",
    # 'versatileimagefield',
    # "django_ratelimit",
]
# VERSATILEIMAGEFIELD_SETTINGS = {
#     'create_images_on_demand': True,
#     'cache_length': 2592000,
# }
LANGUAGE_CODE = "uk"  # Мова за замовчуванням

PARLER_LANGUAGES = {
    None: (
        {"code": "uk", "fallbacks": ["en"], "hide_untranslated": False},
        {"code": "en", "fallbacks": ["uk"], "hide_untranslated": False},
    ),
    "default": {
        "fallbacks": ["uk"],
        "hide_untranslated": False,
    },
}

PARLER_LANGUAGES_LIST = [lang.get("code") for lang in PARLER_LANGUAGES.get(None, [])]

GLOBAL_LANGUAGES = [
    ("uk", "Ukrainian"),
    ("en", "English"),
]
USE_I18N = True
USE_L10N = True


LANGUAGES = []
for lang in GLOBAL_LANGUAGES:
    if lang[0] in PARLER_LANGUAGES_LIST:
        LANGUAGES.append(lang)

# Для локалізації шаблонів і API
LOCALE_PATHS = [
    BASE_DIR / "locale",
]
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE", default=True, cast=bool)
SESSION_COOKIE_HTTPONLY = env("SESSION_COOKIE_HTTPONLY", default=True, cast=bool)
SESSION_COOKIE_SAMESITE = env(
    "SESSION_COOKIE_SAMESITE", default="Lax", cast=str
)  # Lax for same-origin requests, None for cross-origin
SESSION_COOKIE_AGE = env(
    "SESSION_COOKIE_AGE", default=60 * 60 * 24 * 30, cast=int
)  # 30 days


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "addons.middleware.AdminSplitterSessionMiddleware",
    # "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    # "django_ratelimit.middleware.RatelimitMiddleware",
]
# RATELIMIT_VIEW = 'yourapp.views.rate_limited'


ROOT_URLCONF = "project_1444.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "django.template.context_processors.i18n",
            ],
        },
    },
]

WSGI_APPLICATION = "project_1444.wsgi.application"

# Налаштування автентифікації
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

# URL для перенаправлення після логіну/логоуту
LOGIN_URL = "auth/login/"
# LOGIN_REDIRECT_URL = "user/profile/"
LOGOUT_REDIRECT_URL = "/admin/login/"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'neondb',
#         'USER': 'your_user',
#         'PASSWORD': 'your_password',
#         'HOST': 'your_neon_host',
#         'PORT': '5432',
#     },
#     'test': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'test_db.sqlite3',
#     }
# }
try:
    if not env("DATABASE_URL", default=None):
        raise environ.ImproperlyConfigured
    DATABASES = {"default": env.db()}
except environ.ImproperlyConfigured:
    try:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": env("DATABASE_NAME"),
                "USER": env("DATABASE_USER"),
                "PASSWORD": env("DATABASE_PASSWORD"),
                "HOST": env("DATABASE_HOST"),
                "PORT": env("DATABASE_PORT", default=5432),
            }
        }
    except environ.ImproperlyConfigured as e:
        print(
            "Database .env setting must have DATABASE_URL or set of DATABASE_HOST, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD:",
            e,
        )
        raise ValueError(e)

if IS_TESTING:
    print("Test mode detected: using a SQLite DB for diagnostics")
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
    }
    SAVE_TEST_DB_OUTPUT = env("SAVE_TEST_DB_OUTPUT", default=False)
    if SAVE_TEST_DB_OUTPUT:
        DATABASES["default"]["TEST"] = {"NAME": "test_db.sqlite3"}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
# AUTH_USER_MODEL = 'users.User'
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

LANGUAGE_CODE = "uk"
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = "Europe/Kyiv"

RECAPTCHA_PUBLIC_KEY = env("RECAPTCHA_PUBLIC_KEY", default=None)
RECAPTCHA_PRIVATE_KEY = env("RECAPTCHA_PRIVATE_KEY", default=None)
# settings.py

STATIC_URL = env("STATIC_URL", default="/static/")  # 'static/'

STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


for lang in PARLER_LANGUAGES_LIST:
    for locale in LOCALE_PATHS:
        lang_locale = locale / lang
        if not lang_locale.exists():
            lang_locale.mkdir(parents=True)
DEFAULT_FILE_STORAGE = None
DEFAULT_FILE_STORAGE_OPTIONS = {}
# Try Cloudinary configuration first
CLOUDINARY_PREVIEW_TRANSFORMATION = env(
    "CLOUDINARY_PREVIEW_TRANSFORMATION", default="c_thumb,g_face,h_150,w_150"
)
CLOUDINARY_CLOUD_NAME = None
if CLOUDINARY_URL := env("CLOUDINARY_URL", default=None):
    try:
        CLOUDINARY_URL = CLOUDINARY_URL.rstrip("/")
        cl_url = urlparse(CLOUDINARY_URL)
        if cl_url.scheme == "cloudinary":
            CLOUDINARY_NAME = cl_url.hostname
            CLOUDINARY_API_KEY = cl_url.username
            CLOUDINARY_API_SECRET = cl_url.password
            if not all([CLOUDINARY_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
                raise ValueError(
                    "CLOUDINARY_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET must be set"
                )
        else:
            raise ValueError("cloudinary scheme not found in CLOUDINARY_URL")
        CLOUDINARY_MEDIA_TAG = env("CLOUDINARY_MEDIA_TAG", default=PROJECT_NAME)

        DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
        MEDIA_URL = f"{PROJECT_NAME}/"
        CLOUDINARY_STORAGE = {
            "CLOUD_NAME": CLOUDINARY_NAME,
            "API_KEY": CLOUDINARY_API_KEY,
            "API_SECRET": CLOUDINARY_API_SECRET,
            "MEDIA_TAG": CLOUDINARY_MEDIA_TAG,
        }
        CLOUDINARY_CLOUD_NAME = CLOUDINARY_NAME
        INSTALLED_APPS.insert(0, "cloudinary_storage")
    except (KeyError, environ.ImproperlyConfigured, ImportError) as e:
        print(
            "CLOUDINARY not configured correctly by environs. Can setup CLOUDINARY_URL, or their components. Error:",
            str(e),
        )
else:
    # Фаллбек на FileSystemStorage, якщо Cloudinary не налаштовано
    print("Cloudinary not configured. Using FileSystemStorage as DEFAULT_FILE_STORAGE")
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    # DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"


CLOUDINARY_FIXED_PREFIX_PATH_ACCOUNT = env(
    "CLOUDINARY_FIXED_PREFIX_PATH_ACCOUNT",
    default=CLOUDINARY_CLOUD_NAME,
)

CLOUDINARY_IMAGE_FIXED_PREFIX_PATH = env(
    "CLOUDINARY_FIXED_PREFIX_PATH",
    default=(
        f"https://res.cloudinary.com/{CLOUDINARY_FIXED_PREFIX_PATH_ACCOUNT}/image/upload/"
        if CLOUDINARY_FIXED_PREFIX_PATH_ACCOUNT
        else ""
    ),
)

CLOUDINARY_FILE_FIXED_PREFIX_PATH = env(
    "CLOUDINARY_FIXED_PREFIX_PATH",
    default=(
        f"https://res.cloudinary.com/{CLOUDINARY_FIXED_PREFIX_PATH_ACCOUNT}/file/upload/"
        if CLOUDINARY_FIXED_PREFIX_PATH_ACCOUNT
        else ""
    ),
)

if IS_TESTING:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.InMemoryStorage"
    PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]

# Налаштування STORAGES
STORAGES = {
    "default": {
        "BACKEND": DEFAULT_FILE_STORAGE,
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Логування конфігурації
if DEFAULT_FILE_STORAGE:
    print(f"Using DEFAULT_FILE_STORAGE BACKEND: '{DEFAULT_FILE_STORAGE}'")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "cloudinary": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "users": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "utils": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}
# CLOUDINARY_PREVIEW_TRANSFORMATION = env(
#     "CLOUDINARY_PREVIEW_TRANSFORMATION", default="c_thumb,g_face,h_150,w_150"
# )
# if CLOUDINARY_URL := env("CLOUDINARY_URL", default=None):
#     try:
#         # CLOUDINARY_URL = env("CLOUDINARY_URL")
#         CLOUDINARY_URL = CLOUDINARY_URL.rstrip("/")
#         cl_url = urlparse(CLOUDINARY_URL)
#         if cl_url.scheme == "cloudinary":
#             CLOUDINARY_NAME = cl_url.hostname
#             CLOUDINARY_API_KEY = cl_url.username
#             CLOUDINARY_API_SECRET = cl_url.password
#             if not all([CLOUDINARY_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
#                 raise ValueError(
#                     "CLOUDINARY_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET must be set"
#                 )
#         else:
#             raise ValueError("cloudinary scheme not found in CLOUDINARY_URL")
#         CLOUDINARY_MEDIA_TAG = env("CLOUDINARY_MEDIA_TAG", default=PROJECT_NAME)

#         DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
#         # MEDIA_URL = f"https://res.cloudinary.com/{CLOUDINARY_NAME}/"
#         MEDIA_URL = f"{PROJECT_NAME}/"
#         CLOUDINARY_STORAGE = {
#             "CLOUD_NAME": CLOUDINARY_NAME,
#             "API_KEY": CLOUDINARY_API_KEY,
#             "API_SECRET": CLOUDINARY_API_SECRET,
#             "MEDIA_TAG": CLOUDINARY_MEDIA_TAG,
#         }
#         INSTALLED_APPS.insert(0, "cloudinary_storage")
#     except (KeyError, environ.ImproperlyConfigured, ImportError) as e:
#         print(
#             "CLOUDINARY not configured correctly by environs. Can setup CLOUDINARY_URL, or their components.  Error:",
#             str(e),
#         )

# if not DEFAULT_FILE_STORAGE and env("AWS_ACCESS_KEY_ID", default=None):
#     # Try S3 / MinIO / ... configuration
#     try:
#         AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
#         AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
#         AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
#         AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default=None)  # optional
#         AWS_S3_ENDPOINT_URL = env(
#             "AWS_S3_ENDPOINT_URL",
#             default=f"https://{AWS_STORAGE_BUCKET_NAME}.s3{AWS_S3_REGION_NAME if AWS_S3_REGION_NAME else '.'}.amazonaws.com/",
#         )
#         AWS_LOCATION = env("AWS_LOCATION", default="")
#         AWS_S3_VERIFY = env("AWS_S3_VERIFY", default=None, cast=bool)

#         DEFAULT_FILE_STORAGE = "storages.backends.s3.S3Storage"
#         DEFAULT_FILE_STORAGE_OPTIONS = {
#             "access_key": AWS_ACCESS_KEY_ID,
#             "secret_key": AWS_SECRET_ACCESS_KEY,
#             "bucket_name": AWS_STORAGE_BUCKET_NAME,
#             "region_name": AWS_S3_REGION_NAME,
#             "endpoint_url": AWS_S3_ENDPOINT_URL,
#             "location": AWS_LOCATION,
#             "verify": AWS_S3_VERIFY,
#         }
#     except (KeyError, environ.ImproperlyConfigured) as e:
#         print(
#             "AWS S3 / MinIO not configured correctly by environs. Error:",
#             str(e),
#         )

# if DEFAULT_FILE_STORAGE:
#     print(f"Using DEFAULT_FILE_STORAGE BACKEND: '{DEFAULT_FILE_STORAGE}'")
#     STORAGES = {
#         "default": {
#             "BACKEND": DEFAULT_FILE_STORAGE,
#             "OPTIONS": DEFAULT_FILE_STORAGE_OPTIONS,
#         },
#         "staticfiles": {
#             "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
#         },
#     }

# STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"  # for compatibility with cloudinary static files

# # Fallback for use FileSystemStorage when CLOUDINARY, or S3 / MinIO not configured
# if not DEFAULT_FILE_STORAGE:
#     print(f"Using FileSystemStorage as DEFAULT_FILE_STORAGE BACKEND")
# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / "emails"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

try:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = env("EMAIL_HOST")
    EMAIL_PORT = env("EMAIL_PORT", cast=int, default=465)
    EMAIL_USE_SSL = env("EMAIL_USE_SSL", cast=bool, default=True)
    EMAIL_HOST_USER = env("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
    DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)
    if not EMAIL_HOST:
        EMAIL_BACKEND = None
except (KeyError, environ.ImproperlyConfigured):
    EMAIL_BACKEND = None

ANON_RATE_THROTTLE = env("ANON_RATE_THROTTLE", default="5/minute") or None
USER_RATE_THROTTLE = env("USER_RATE_THROTTLE", default="10/minute") or None
print(f"{ANON_RATE_THROTTLE=}, {USER_RATE_THROTTLE=}")

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        # "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": ANON_RATE_THROTTLE, "user": USER_RATE_THROTTLE},
}

if IS_TESTING:
    REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
    REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {"anon": None, "user": None}


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}


CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_ALL_ORIGINS = not CORS_ALLOWED_ORIGINS
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

CSRF_COOKIE_HTTPONLY = False  # needed so JS can read the cookie
CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True

print(f"{CSRF_TRUSTED_ORIGINS=}")

GIT_VERSION = env("GIT_VERSION", default="Version is unknown")
VERSION = env("VERSION", default=__version__)
CACHE_HEADERS_ENABLED = env("CACHE_HEADERS_ENABLED", default=False, cast=bool)

REDIS_URL = env("REDIS_URL", default=None)

if REDIS_URL:
    import redis

    try:
        r = redis.Redis.from_url(REDIS_URL)
        r.ping()
        CACHES = {
            "default": {
                # "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": REDIS_URL,
            }
        }
        SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
    except redis.ConnectionError as e:
        print(f"Can't connect to Redis {REDIS_URL}, skip of use Redis: {e}")

# CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
# CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TIMEZONE = 'Europe/Kyiv'

CELERY_BROKER_URL = env(
    "CELERY_BROKER_URL", default=None
)  # Redis як брокер повідомлень
if not CELERY_BROKER_URL:
    CELERY_BROKER_URL = REDIS_URL or "redis://localhost:6379/0"

CELERY_RESULT_BACKEND = env(
    "CELERY_RESULT_BACKEND", default=None
)  # Redis як брокер повідомлень
if not CELERY_RESULT_BACKEND:
    CELERY_RESULT_BACKEND = CELERY_BROKER_URL or REDIS_URL or "redis://localhost:6379/0"

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE or "Europe/Kyiv"

SQL_CACHE_TIMEOUT_DEFAULT = env(
    "SQL_CACHE_TIMEOUT_DEFAULT", default=60 * 60 * 1
)  # 1 hour

# print(f"{CORS_ALLOWED_ORIGINS=}, {CORS_ALLOW_ALL_ORIGINS=}, {CSRF_TRUSTED_ORIGINS=}")
LIQPAY_PUBLIC_KEY = env("LIQPAY_PUBLIC_KEY", default="your-public-key")
LIQPAY_PRIVATE_KEY = env("LIQPAY_PRIVATE_KEY", default="your-private-key")
LIQPAY_DEFAULT_CURRENCY = env("LIQPAY_DEFAULT_CURRENCY", default="UAH")
LIQPAY_DEFAULT_LANGUAGE = env("LIQPAY_DEFAULT_LANGUAGE", default="uk")
LIQPAY_DEFAULT_ACTION = env("LIQPAY_DEFAULT_ACTION", default="pay")
LIQPAY_SANDBOX_MODE = env("LIQPAY_SANDBOX_MODE", default=True, cast=bool)

# Social external auth
# Google Auth
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = (
    env("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY", default=None) or None
)
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = (
    env("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET", default=None) or None
)
if all([SOCIAL_AUTH_GOOGLE_OAUTH2_KEY, SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET]):
    AUTHENTICATION_BACKENDS.append("social_core.backends.google.GoogleOAuth2")

# Apple ID Auth, Cost $99 per year
SOCIAL_AUTH_APPLE_ID_CLIENT = env("SOCIAL_AUTH_APPLE_ID_CLIENT", default=None) or None
SOCIAL_AUTH_APPLE_ID_TEAM = env("SOCIAL_AUTH_APPLE_ID_TEAM", default=None) or None
SOCIAL_AUTH_APPLE_ID_KEY = env("SOCIAL_AUTH_APPLE_ID_KEY", default=None) or None
SOCIAL_AUTH_APPLE_ID_SECRET = env("SOCIAL_AUTH_APPLE_ID_SECRET", default=None) or None
SOCIAL_AUTH_APPLE_ID_SCOPE = ["name", "email"]
if all([SOCIAL_AUTH_APPLE_ID_CLIENT, SOCIAL_AUTH_APPLE_ID_SECRET]):
    AUTHENTICATION_BACKENDS.append("social_core.backends.apple.AppleIdAuth")

# GitHub auth
SOCIAL_AUTH_GITHUB_KEY = env("SOCIAL_AUTH_GITHUB_KEY", default=None) or None
SOCIAL_AUTH_GITHUB_SECRET = env("SOCIAL_AUTH_GITHUB_SECRET", default=None) or None
SOCIAL_AUTH_GITHUB_SCOPE = ["user:email", "read:user"]
if all([SOCIAL_AUTH_GITHUB_KEY, SOCIAL_AUTH_GITHUB_SECRET]):
    AUTHENTICATION_BACKENDS.append("social_core.backends.github.GithubOAuth2")

# Linkedin auth
SOCIAL_AUTH_LINKEDIN_OPENIDCONNECT_KEY = (
    env("SOCIAL_AUTH_LINKEDIN_OPENIDCONNECT_KEY", default=None) or None
)
SOCIAL_AUTH_LINKEDIN_OPENIDCONNECT_SECRET = (
    env("SOCIAL_AUTH_LINKEDIN_OPENIDCONNECT_SECRET", default=None) or None
)
SOCIAL_AUTH_LINKEDIN_OPENIDCONNECT_USERNAME_IS_FULL_EMAIL = True
if all(
    [SOCIAL_AUTH_LINKEDIN_OPENIDCONNECT_KEY, SOCIAL_AUTH_LINKEDIN_OPENIDCONNECT_SECRET]
):
    AUTHENTICATION_BACKENDS.append(
        "social_core.backends.linkedin.LinkedinOpenIdConnect"
    )
# Facebook auth
SOCIAL_AUTH_FACEBOOK_KEY = env("SOCIAL_AUTH_FACEBOOK_KEY", default=None) or None
SOCIAL_AUTH_FACEBOOK_SECRET = env("SOCIAL_AUTH_FACEBOOK_SECRET", default=None) or None
SOCIAL_AUTH_FACEBOOK_SCOPE = ["email"]
if all([SOCIAL_AUTH_FACEBOOK_KEY, SOCIAL_AUTH_FACEBOOK_SECRET]):
    AUTHENTICATION_BACKENDS.append("social_core.backends.facebook.FacebookOAuth2")

SOCIAL_AUTH_LOGIN_ERROR_URL = reverse_lazy("admin:login")
# LOGIN_ERROR_URL = "/admin/login/?auth_error=1"
SOCIAL_AUTH_JSONFIELD_ENABLED = True
# SOCIAL_AUTH_REQUIRE_POST = True
# SOCIAL_AUTH_PIPELINE = (
#     "social_core.pipeline.social_auth.social_user",  # Link social user to Django user
#     "social_core.pipeline.social_auth.associate_by_email",  # Associate by email if available
#     "social_core.pipeline.social_auth.load_extra_data",  # Load extra data from the social provider
#     "social_core.pipeline.user.user_details",  # Update user details (name, etc.)
#     "users.signals.set_username_from_email",  # Custom step to set email as the username
# )
SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. In some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    "social_core.pipeline.social_auth.social_details",
    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    "social_core.pipeline.social_auth.social_uid",
    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    "social_core.pipeline.social_auth.auth_allowed",
    # Checks if the current social-account is already associated in the site.
    "social_core.pipeline.social_auth.social_user",
    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    "social_core.pipeline.user.get_username",
    # Send a validation email to the user to verify its email address.
    # Disabled by default.
    # 'social_core.pipeline.mail.mail_validation',
    # Associates the current social details with another user account with
    # a similar email address. Disabled by default.
    "social_core.pipeline.social_auth.associate_by_email",
    # Create a user account if we haven't found one yet.
    "social_core.pipeline.user.create_user",
    # For new users copy avatar url to profile of user
    "users.utils.set_profile_avatar_from_social",
    # Create the record that associates the social account with the user.
    "social_core.pipeline.social_auth.associate_user",
    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    "social_core.pipeline.social_auth.load_extra_data",
    # Update the user record with any changed info from the auth service.
    "social_core.pipeline.user.user_details",
    "users.utils.mark_social_login",
    "users.utils.mark_social_login",
    "users.utils.mark_social_login",
)
SOCIAL_AUTH_SANITIZE_REDIRECTS = True
SOCIAL_AUTH_LOGIN_REDIRECT_URL = f"{SITE_URL}/social-auth/token/"
SOCIAL_AUTH_FORCE_LOGOUT_AFTER_TOKEN = env(
    "SOCIAL_AUTH_FORCE_LOGOUT_AFTER_TOKEN", default=True
)

# Allowed messengers
ALLOWED_MESSENGERS = ["viber", "telegram", "whatsapp", "signal", "discord"]
INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]
OTP_EXPIRATION_TIME = 15  # minutes
# INSTALLED_APPS = [
#     ...,
#     'django_ratelimit',
# ]

# MIDDLEWARE = [
#     ...,
#     'ratelimit.middleware.RatelimitMiddleware',
# ]

# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         }
#     }
# }

# RATELIMIT_VIEW = 'users.views.rate_limited'
# RATELIMIT_CACHE_BACKEND = 'default'
# project_1444/settings.py


# REST_FRAMEWORK = {
#     'DEFAULT_THROTTLE_CLASSES': [
#         'rest_framework.throttling.AnonRateThrottle',
#         'rest_framework.throttling.UserRateThrottle'
#     ],
#     'DEFAULT_THROTTLE_RATES': {
#         'anon': '5/minute',
#         'user': '10/minute'
#     }
# }

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#     }
# }

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         '': {
#             'handlers': ['console'],
#             'level': 'INFO',
#         },
#     },
# }
