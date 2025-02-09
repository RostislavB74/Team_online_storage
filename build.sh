#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install --upgrade pip -q  --no-input
pip install -r requirements.txt -q  --no-input
pip install gunicorn -q --no-input

#poetry install -n
#poetry install --with deploy -n

# Convert static asset files
pushd project_1444
export PYTHONPATH=.

python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

# Used env DJANGO_SUPERUSER_PASSWORD
python manage.py createsuperuser --username admin --email admin@localhost --no-input

# DEV ONLY, CRUD
python manage.py populate_base_values

# DEMO USERS AND GROUPS CREATE
python ./utils/create_groups.py
python ./utils/create_admin_user.py


#python manage.py runserver --insecure --noreload

popd > /dev/null

#python -m gunicorn --chdir ./project_1345 project_1345.wsgi:application