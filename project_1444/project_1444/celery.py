# import os
# from celery import Celery
# from celery.schedules import crontab


# app = Celery("project_1444")
# app.config_from_object("django.conf:settings", namespace="CELERY")
# app.autodiscover_tasks()


# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

# app.conf.beat_schedule = {
#     "clear_old_carts": {
#         "task": "cart.tasks.clear_old_carts",
#         "schedule": crontab(hour=3, minute=0),  # Щодня о 3:00
#     },
# }
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_1444.settings")

app = Celery("project_1444")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
