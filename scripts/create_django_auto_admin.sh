#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

if command -v dos2unix &> /dev/null; then
  echo "converting *.sh files from CRLF to LF"
  dos2unix *.sh &> /dev/null
fi

pushd "../project_1444"
export PYTHONPATH=.
poetry run python ./utils/create_groups.py
poetry run python ./utils/create_admin_user.py
popd