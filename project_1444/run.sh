#!/usr/bin/env bash

BRANCH_NAME=${BRANCH_NAME:-$(git branch --show-current)}
BRANCH_NAME=${BRANCH_NAME:-$(git branch -r --contains HEAD | grep -v 'HEAD' | head -n 1 | sed 's|origin/||')}
BRANCH_NAME=${BRANCH_NAME:-"deploy_safe"}

export GIT_VERSION="${BRANCH_NAME}-$(git rev-parse --short HEAD)"


script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

python manage.py migrate
python manage.py collectstatic --noinput

# Ensure DEBUG is set
DEBUG=${DEBUG:-False}

if [ "$DEBUG" = "False" ]; then
   python manage.py runserver 0.0.0.0:8000 --noreload --insecure --no-color
  # Run Gunicorn in production
#  gunicorn --bind "0.0.0.0:8000" "project_1444.wsgi:application"
else
  # Run Django development server
  python manage.py runserver 0.0.0.0:8000 --noreload --insecure --no-color
fi
#gunicorn --bind "0.0.0.0:8000" "project_1444.wsgi:application"