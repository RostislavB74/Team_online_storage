#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

if command -v dos2unix &> /dev/null; then
  echo "converting *.sh files from CRLF to LF"
  dos2unix *.sh &> /dev/null 
fi
echo Starting Database Backup to '.database_backup.json' file...
pushd ".."
python -X utf8 project_1444\manage.py dumpdata  --indent 2 -o .database_backup.json
popd