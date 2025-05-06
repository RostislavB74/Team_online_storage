@echo off
PUSHD "../project_1444"
echo .
echo "Starting Celery worker..."
poetry run celery -A project_1444 worker --loglevel=info

REM Optional: Start Celery beat (for scheduled tasks)
REM echo "Starting Celery beat..."
REM celery -A project_1444 beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler &

POPD
