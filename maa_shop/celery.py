import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maa_shop.settings')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1') # for windows only

app = Celery('maa_shop')

app.config_from_object('django.conf:settings', 'CELERY')

app.autodiscover_tasks()