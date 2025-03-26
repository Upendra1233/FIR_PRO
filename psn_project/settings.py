import os
from pathlib import Path
import sys

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

# Define the base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Basic Django settings
DEBUG = True  # Set to False in production for security
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']  # Change this in production to specific domain names
# filepath: psn_project/settings.py
SECRET_KEY = 'XzFm9th2F_hEtuxTrIQif8di1BgcPVT7Ol-XJRJixU_grh8_-T7Q1UesXDlg_JNyb-M'
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'psnapp',  # Your custom app (psnapp)
    'sr_request',
    'mapping_process',
    'crispy_forms',
    'crispy_bootstrap5',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Ensure this line is included
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'psn_project.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# WSGI application
WSGI_APPLICATION = 'psn_project.wsgi.application'

# Database configuration (SQLite used in this example)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # You can change this for production DB like PostgreSQL or MySQL
    }
}

# Password validation
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

# Localization settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'  # Indian time zone
USE_I18N = True
USE_TZ = True

# settings.py

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # This should point to your static directory
]
STATIC_ROOT = BASE_DIR / 'staticfiles'  # This is where collectstatic will store files

# Media files (Uploaded by users)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email settings (to send emails)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mulaupendrareddy@gmail.com'  # Replace with your email address
EMAIL_HOST_PASSWORD = 'wvdf wkoy whiz nvvv'  # Replace with your App Password
DEFAULT_FROM_EMAIL = 'mulaupendrareddy@gmail.com'
EMAIL_SUBJECT_PREFIX = '[FIR Request] '

# For production, use environment variables for sensitive data like passwords
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  # Uncomment to use environment variable
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  # Uncomment to use environment variable

# Site domain (can be used for generating absolute links in emails)
SITE_DOMAIN = '127.0.0.1:8000'  # For local development, change for production

# Logging configuration (write errors to a log file)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'django_error.log',  # Log file
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

# Caching settings (optional, for production setup)
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': '127.0.0.1:11211',
#     }
# }

# CSRF settings (for security)
CSRF_COOKIE_SECURE = True  # Only set this to True if you use HTTPS
SESSION_COOKIE_SECURE = True  # Only set this to True if you use HTTPS

# Security settings (important for production)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CSRF_TRUSTED_ORIGINS to allow access from trusted domains (useful for production)
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000']

# Customize your admin site title and header
ADMIN_SITE_HEADER = 'PSN Project Admin'
ADMIN_SITE_TITLE = 'PSN Admin'

# Manager and HOD email addresses
MANAGER_EMAIL = 'sales@danlawtech.com'  # Manager's email address
HOD_EMAIL = 'rajendrans@danlawtech.com'  # HOD's email address

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

if DEBUG is False:
    from django.conf.urls.static import static
    from django.conf import settings

    urlpatterns = []  # Define urlpatterns as an empty list
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)