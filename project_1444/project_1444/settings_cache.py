import redis
# from pathlib import Path
# from django.core.cache import cache
# import environ
from .settings_base import env

REDIS_URL = env("REDIS_URL", default=None)

if REDIS_URL:
    try:
        r = redis.Redis.from_url(REDIS_URL)
        r.ping()  # перевірка доступності
        CACHES = {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": REDIS_URL,
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                },
            }
        }
        SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
        print(f"✅ Використовую Redis Cache {REDIS_URL}")
    except redis.ConnectionError as e:
        print(f"⚠️ Redis недоступний ({REDIS_URL}), fallback на LocMemCache: {e}")
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
else:
    print("⚠️ REDIS_URL не задано, використовую LocMemCache")
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
