@echo off
echo Starting Django createsuperuser...
PUSHD "../project_1444"
@REM poetry run python manage.py createsuperuser --username admin
poetry run python manage.py createsuperuser --noinput --username admin

POPD