import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.timezone = 'Asia/Bishkek'

app.conf.beat_schedule = {
    'processing-document': {
        'task': 'document.tasks.processing_document',
        'schedule': crontab(minute=0, hour=3),
    }
}
