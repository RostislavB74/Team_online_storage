@echo off
PUSHD "../project_1444"
echo .
@REM echo "Starting Celery worker..."
@REM poetry run celery -A project_1444 worker --loglevel=info

rem Optional: Start Celery beat (for scheduled tasks)
echo "Starting Celery beat..."
celery -A project_1444 beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler

POPD
