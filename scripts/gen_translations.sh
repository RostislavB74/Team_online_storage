#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

pushd "../project_1444"
echo -e "\nStarting Django make locale messages..."
# django-admin makemessages --all
# django-admin compilemessages
poetry run python manage.py makemessages --all
poetry run python manage.py compilemessages
popd