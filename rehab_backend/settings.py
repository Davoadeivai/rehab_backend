"""
Django settings for rehab_backend project.
"""

from pathlib import Path
import os

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security
# IMPORTANT: In production, load the SECRET_KEY from an environment variable or secrets file!
SECRET_KEY = "django-insecure-21m(#k7flv1s-ka3&*_fo&z@a2p&@*sc%xujhmmq=)+b=v5y2_"
# IMPORTANT: DEBUG should be False in production. Load from an environment variable.
DEBUG = True  # در محیط توسعه True باشد
# DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'
# IMPORTANT: In production, ALLOWED_HOSTS should list your specific domain(s). Load from an environment variable.
ALLOWED_HOSTS = ['*']  # در تولید محدود کنید
# ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'yourdomain.com,www.yourdomain.com').split(',') if os.environ.get('DJANGO_ALLOWED_HOSTS') else []

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    
    # Third-party apps
    "django_jalali",
    "rest_framework",
    "rest_framework.authtoken",
    "django_extensions",
    "corsheaders",
    
    # Local apps
    "patients",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "rehab_backend.urls"

# CORS Settings
# IMPORTANT: In production, set CORS_ALLOW_ALL_ORIGINS = False and use CORS_ALLOWED_ORIGINS or CORS_ALLOWED_ORIGIN_REGEX
# to whitelist specific frontend domains. For example:
# CORS_ALLOWED_ORIGINS = [
#     "https://yourfrontenddomain.com",
#     "http://localhost:3000", # If you have a local frontend dev server
# ]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = "rehab_backend.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "health",  # In prod, load from env: os.environ.get('DB_NAME')
        "USER": "mohammad1",  # In prod, load from env: os.environ.get('DB_USER')
        "PASSWORD": "1234",  # In prod, load from env: os.environ.get('DB_PASSWORD')
        "HOST": "localhost",  # In prod, load from env: os.environ.get('DB_HOST')
        "PORT": "5432",  # In prod, load from env: os.environ.get('DB_PORT')
    }
}

# Password validation
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

# Internationalization
LANGUAGE_CODE = "fa-ir"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_L10N = True
# Consider setting USE_TZ = True for robust timezone handling.
# When USE_TZ is True, Django stores datetime information as UTC in the database
# and handles conversions to the local TIME_ZONE ("Asia/Tehran" in this case)
# at the template and form levels. This is generally recommended.
# If False, datetimes are naive and assumed to be in the TIME_ZONE.
USE_TZ = False

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

# Email (مثال برای Gmail)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# IMPORTANT: In production, load EMAIL_HOST_USER and EMAIL_HOST_PASSWORD from environment variables or a secrets file.
# For example:
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-password'