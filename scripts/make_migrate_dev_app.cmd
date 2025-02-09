@echo off
echo ""
echo  "Starting Django makemigrations..."
PUSHD "../project_1444"
poetry run python manage.py makemigrations
POPD