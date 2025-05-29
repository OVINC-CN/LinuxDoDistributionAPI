import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "entry.settings")
os.environ.setdefault("C_FORCE_ROOT", "True")

app = Celery("main", broker=settings.BROKER_URL)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Schedule Tasks
app.conf.beat_schedule = {
    "do_stats": {
        "task": "apps.vcd.tasks.do_stats",
        "schedule": crontab(minute="*/5"),
        "args": (),
    },
    "close_no_stock": {
        "task": "apps.vcd.tasks.close_no_stock",
        "schedule": crontab(minute="*/5"),
        "args": (),
    },
    "sync_blacklist": {
        "task": "apps.tcaptcha.tasks.sync_blacklist",
        "schedule": crontab(minute="*/5"),
        "args": (),
    },
}
