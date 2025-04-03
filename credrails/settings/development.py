from .base import INSTALLED_APPS, MIDDLEWARE

DEBUG = True

SECRET_KEY = "django-insecure-h8o#1=b17-tt(%rig$03h(xgr(@nx1yi(xfs&59h4!w#471$j+"

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += ["debug_toolbar"]

MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

INTERNAL_IPS = type(str("c"), (), {"__contains__": lambda *a: True})()
