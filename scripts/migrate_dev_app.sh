#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

if command -v dos2unix &> /dev/null; then
#  echo "converting *.sh files from CRLF to LF"
  dos2unix *.sh &> /dev/null
fi

echo -e "\nStarting Django migrate..."
pushd "../project_1444" > /dev/null
poetry run python manage.py migrate $@
popd > /dev/null