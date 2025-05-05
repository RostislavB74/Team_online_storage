@echo off
PUSHD "../project_1444"
echo .
echo Starting Django Build schema.yaml ...
poetry run python manage.py spectacular --file schema.yaml
POPD
