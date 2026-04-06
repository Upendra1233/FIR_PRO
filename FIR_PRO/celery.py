import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FIR_PRO.settings')

app = Celery('FIR_PRO')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()