@echo off
echo ""
echo  "Starting Django test..."
PUSHD "../project_1444"
SET apps="product"
poetry run python manage.py test %apps% --keepdb -v 2
POPD