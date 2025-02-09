@echo off
PUSHD "../project_1444"
set PYTHONPATH=.
poetry run python ./utils/create_groups.py
poetry run python ./utils/create_admin_user.py
POPD