#!/usr/bin/env bash
# Exit on error
set -o errexit

pushd project_1444

python manage.py runserver --insecure --noreload 0.0.0.0:8000

popd > /dev/null
