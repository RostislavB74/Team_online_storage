@echo off
PUSHD "../project_1444"
echo .
echo Starting Django collectstatic...
poetry run python manage.py collectstatic --noinput
POPD
