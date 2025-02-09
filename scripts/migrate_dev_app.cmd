@echo off
echo.
echo Starting Django migrate...
PUSHD "../project_1444"
poetry run python manage.py migrate %1 %2
POPD