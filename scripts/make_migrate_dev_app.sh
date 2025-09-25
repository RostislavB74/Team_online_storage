#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

if command -v dos2unix &> /dev/null; then
  echo "converting *.sh files from CRLF to LF"
  dos2unix *.sh &> /dev/null
fi

echo PYTHONPATH=${PYTHONPATH}
pushd "../project_1444"
echo -e "\nStarting Django makemigrations..."
poetry run python manage.py makemigrations
popd