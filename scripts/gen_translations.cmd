@echo off
PUSHD "../project_1444"
echo .
echo Starting Django make locale messages...
@REM django-admin makemessages --all
@REM django-admin compilemessages
poetry run python manage.py makemessages --all
poetry run python manage.py compilemessages
POPD
