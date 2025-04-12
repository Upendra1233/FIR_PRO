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

BASE_DIR = Path(__file__).resolve().parent.parent


DEBUG = True 
ALLOWED_HOSTS = ['127.0.0.1', 'localhost'] 

SECRET_KEY = 'XzFm9th2F_hEtuxTrIQif8di1BgcPVT7Ol-XJRJixU_grh8_-T7Q1UesXDlg_JNyb-M'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'psnapp',  # fir page-1
    'sr_request', # Sr-request page-3
    'mapping_process',  #mp -page -2
    'direct_calls',     #calls -page 4
    'billing_data',    #billing -page 5
    'crispy_forms',
    'crispy_bootstrap5',
    'accounts',  # Add the accounts app here
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
 # Add the custom middleware here
]

ROOT_URLCONF = 'psn_project.urls'


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




STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',  
]
STATIC_ROOT = BASE_DIR / 'staticfiles'  

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mulaupendrareddy@gmail.com' 
EMAIL_HOST_PASSWORD = 'wvdf wkoy whiz nvvv'  
DEFAULT_FROM_EMAIL = 'mulaupendrareddy@gmail.com'
EMAIL_SUBJECT_PREFIX = '[FIR Request] '


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

if DEBUG is False:
    from django.conf.urls.static import static
    from django.conf import settings

    urlpatterns = []  
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)