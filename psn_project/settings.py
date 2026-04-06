import os
from pathlib import Path
import sys
from celery.schedules import crontab

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psn_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()

BASE_DIR = Path(__file__).resolve().parent.parent


DEBUG = True 
ALLOWED_HOSTS = ['127.0.0.1', 'localhost'] 

SECRET_KEY = 'XzFm9th2F_hEtuxTrIQif8di1BgcPVT7Ol-XJRJixU_grh8_-T7Q1UesXDlg_JNyb-M'
# filepath: c:\Users\Admin\Desktop\FIR_PRO\settings.py
# CUSTOMER PORTAL config: prefer env vars; provide sensible defaults during DEBUG for local testing.
CUSTOMER_PORTAL_URL = os.environ.get('CUSTOMER_PORTAL_URL', '').strip()
CUSTOMER_PORTAL_TOKEN = os.environ.get('CUSTOMER_PORTAL_TOKEN', '').strip()

# If running in DEBUG and no real URL is configured, use a test endpoint (httpbin) so submits can be exercised locally.
if DEBUG and not CUSTOMER_PORTAL_URL:
    CUSTOMER_PORTAL_URL = os.environ.get('CUSTOMER_PORTAL_DEV_URL', 'https://httpbin.org/post')
    if not CUSTOMER_PORTAL_TOKEN:
        CUSTOMER_PORTAL_TOKEN = os.environ.get('CUSTOMER_PORTAL_DEV_TOKEN', 'testtoken')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'psnapp',  
    'sr_request', 
    'mapping_process',  
    'direct_calls',    
    'billing_data',    
    'crispy_forms',
    'crispy_bootstrap5',
    'accounts',  
    'AIS140_FLOW',
    'sat_leave',
    'data_search',
    'bill_verify',
    'trip_app',
    'rest_framework',
    'rest_framework.authtoken',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    # insert site auth middleware AFTER SessionMiddleware
    "psn_project.middleware.SiteAuthMiddleware",
]

ROOT_URLCONF = 'psn_project.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Add your global templates directory here
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

# WSGI application path 
WSGI_APPLICATION = 'psn_project.wsgi.application'

# Database configuration (SQLite used in this example) need  to change while produ
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'  # Set timezone to IST
USE_I18N = True
USE_TZ = True  # Enable timezone support




# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# EMAIL CONFIGURATION - Default for FIR_PRO and other projects
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'crscdanlaw@danlawtechnologies.com'
EMAIL_HOST_PASSWORD = 'byvdrxyvyfcjozhe'   # no spaces

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_SUBJECT_PREFIX = '[FIR Request] '

# AIS140 FLOW - Separate Email Configuration
AIS140_EMAIL_CONFIG = {
    'EMAIL_HOST': 'smtp.gmail.com',
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_HOST_USER': 'ais140danlaw@danlawtechnologies.com',
    'EMAIL_HOST_PASSWORD': 'sumj ytxh buxf fpra',
    'DEFAULT_FROM_EMAIL': 'ais140danlaw@danlawtechnologies.com',
}

# FIR PROJECT - Default Email Configuration
# FIR PROJECT - Default Email Configuration
FIR_EMAIL_CONFIG = {
    'EMAIL_HOST': 'smtp.gmail.com',
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_HOST_USER': 'crscdanlaw@danlawtechnologies.com',
    'EMAIL_HOST_PASSWORD': 'byvd rxyv yfcj ozhe',
    'DEFAULT_FROM_EMAIL': 'crscdanlaw@danlawtechnologies.com',
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ]
}

SITE_DOMAIN = '127.0.0.1:8000' 

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'django_error.log',  
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}


CSRF_COOKIE_SECURE = True  
SESSION_COOKIE_SECURE = True  # Only set this to True if when we use HTTPS

#
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'


CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000']


ADMIN_SITE_HEADER = 'PSN Project Admin'
ADMIN_SITE_TITLE = 'PSN Admin'

# Manager and HOD email addresses
MANAGER_EMAIL = 'sales@danlawtech.com'  
HOD_EMAIL = 'rajendrans@danlawtech.com'  

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

import os
TWILIO_ACCOUNT_SID = os.environ.get('AC2e99053af77e25c07b9abf13931ed2fa')
TWILIO_AUTH_TOKEN = os.environ.get('8a6b4351663a6e871994fc2f7ab7ce7c')
TWILIO_FROM_NUMBER = os.environ.get('+916303908940')  # e.g. '+1234567890'

# Shared credentials (use env vars in production)
ENGINEER_USERNAME = os.environ.get("ENGINEER_USERNAME", "engineer")
ENGINEER_PASSWORD = os.environ.get("ENGINEER_PASSWORD", "ChangeMe123!")

LOGIN_URL = "/login/"

if DEBUG is False:
    from django.conf.urls.static import static
    from django.conf import settings

    urlpatterns = []  
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# psn_project/settings.py — add Redis cache config# gunicorn_config.py
bind = "0.0.0.0:8000"
workers = 4  # (2 * CPU_count) + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 5# gunicorn_config.py
bind = "0.0.0.0:8000"
workers = 4  # (2 * CPU_count) + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 5# gunicorn_config.py
bind = "0.0.0.0:8000"
workers = 4  # (2 * CPU_count) + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 5

# Use simple in-memory cache for development (no Redis needed)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'fir-pro-cache',
    }
}

# Use database-backed sessions instead of Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

CELERY_BEAT_SCHEDULE = {
    'generate-daily-reports': {
        'task': 'direct_calls.tasks.generate_daily_reports_task',
        'schedule': crontab(hour=0, minute=0),  # Run at midnight
    },
}

# Security for production
if not DEBUG:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'your-domain.com']
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Gunicorn
GUNICORN_CMD_ARGS = '--workers=4 --bind=127.0.0.1:8000 --timeout=30'

# Celery (if not already configured)
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'db+sqlite:///celery.db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TASK_ALWAYS_EAGER = True  # Execute tasks immediately (for dev)