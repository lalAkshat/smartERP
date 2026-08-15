"""
Django settings for config project.
"""

import os
from pathlib import Path

import dj_database_url


# =====================================================
# BASE DIRECTORY
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =====================================================
# SECURITY
# =====================================================

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"


# Render automatically provides this variable
RENDER_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]

if RENDER_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_HOSTNAME)


# =====================================================
# APPLICATIONS
# =====================================================

INSTALLED_APPS = [

    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Your apps
    "employees",
    "accounts",
]


# =====================================================
# MIDDLEWARE
# =====================================================

MIDDLEWARE = [

    "django.middleware.security.SecurityMiddleware",

    # Static files in production
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =====================================================
# URL CONFIGURATION
# =====================================================

ROOT_URLCONF = "config.urls"


# =====================================================
# TEMPLATES
# =====================================================

TEMPLATES = [

    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [

                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# =====================================================
# WSGI
# =====================================================

WSGI_APPLICATION = "config.wsgi.application"


# =====================================================
# DATABASE
# =====================================================

# Render will provide DATABASE_URL.
#
# Locally, if DATABASE_URL is not available,
# Django will use your local MySQL database.

DATABASES = {

    "default": dj_database_url.config(

        default=(
            f"mysql://"
            f"{os.getenv('MYSQL_USER', 'smarterp_user')}:"
            f"{os.getenv('MYSQL_PASSWORD', 'Nilam@123')}@"
            f"{os.getenv('MYSQL_HOST', 'localhost')}:"
            f"{os.getenv('MYSQL_PORT', '3306')}/"
            f"{os.getenv('MYSQL_DATABASE', 'smarterp')}"
        ),

        conn_max_age=600,
    )
}


# =====================================================
# PASSWORD VALIDATION
# =====================================================

AUTH_PASSWORD_VALIDATORS = [

    {
        "NAME":
        "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },

    {
        "NAME":
        "django.contrib.auth.password_validation.MinimumLengthValidator",
    },

    {
        "NAME":
        "django.contrib.auth.password_validation.CommonPasswordValidator",
    },

    {
        "NAME":
        "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# =====================================================
# INTERNATIONALIZATION
# =====================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# =====================================================
# STATIC FILES
# =====================================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


STORAGES = {

    "default": {
        "BACKEND":
        "django.core.files.storage.FileSystemStorage",
    },

    "staticfiles": {
        "BACKEND":
        "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# =====================================================
# EMAIL
# =====================================================

EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend"
)


# =====================================================
# LOGIN
# =====================================================

LOGIN_URL = "/accounts/login/"


# =====================================================
# SECURITY SETTINGS FOR PRODUCTION
# =====================================================

if not DEBUG:

    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )

    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_HSTS_SECONDS = 31536000

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = True


# =====================================================
# CSRF
# =====================================================

CSRF_TRUSTED_ORIGINS = []

if RENDER_HOSTNAME:

    CSRF_TRUSTED_ORIGINS.append(
        f"https://{RENDER_HOSTNAME}"
    )


# =====================================================
# DEFAULT PRIMARY KEY
# =====================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"