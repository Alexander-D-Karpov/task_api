from .base import *  # noqa: F403
from .base import env

DEBUG = False
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="C77n1xfCim5K8vgaU57QYyR9cMLDpN1HhNufhhcLt3R8Dw6b84rSPyNCqccF96P5",
)

TEST_RUNNER = "django.test.runner.DiscoverRunner"

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

TEMPLATES[0]["OPTIONS"]["debug"] = True  # noqa: F405

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# Use in-memory SQLite for tests (much faster and isolated)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": True,
    }
}
