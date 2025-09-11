@echo off
echo Starting Database Backup to '.database_backup.json' file...
PUSHD ".."
python -X utf8 project_1444\manage.py dumpdata  --indent 2 -o .database_backup.json
POPD