#!/usr/bin/env bash

BRANCH_NAME=${BRANCH_NAME:-$(git branch --show-current)}
BRANCH_NAME=${BRANCH_NAME:-$(git branch -r --contains HEAD | grep -v 'HEAD' | head -n 1 | awk '{print $1}')}
BRANCH_NAME=${BRANCH_NAME:-"deploy_safe"}
BRANCH_NAME=${BRANCH_NAME#origin/}  # Remove 'origin/' if it exists

export GIT_VERSION="${BRANCH_NAME}-$(git rev-parse --short HEAD)"
echo "GIT_VERSION=${GIT_VERSION}"

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

python manage.py migrate
python manage.py collectstatic --noinput

# Ensure DEBUG is set
DEBUG=${DEBUG:-False}

# Start Celery worker in background
echo "Starting Celery worker..."
celery -A project_1444 worker --loglevel=info  -c 1 --max-memory-per-child 131072 --max-tasks-per-child 50 &

# Optional: Start Celery beat (for scheduled tasks)
#echo "Starting Celery beat..."
#celery -A project_1444 beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler &

# Show free system memory info
free -h

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn --bind "0.0.0.0:8000" "project_1444.wsgi:application"

#if [ "$DEBUG" = "False" ]; then
#  # python manage.py runserver 0.0.0.0:8000 --noreload --insecure --no-color
#  # Run Gunicorn in production
#  gunicorn --bind "0.0.0.0:8000" "project_1444.wsgi:application"
#else
#  # Run Django development server
#  python manage.py runserver 0.0.0.0:8000 --noreload --insecure --no-color
#fi

#gunicorn --bind "0.0.0.0:8000" "project_1444.wsgi:application"