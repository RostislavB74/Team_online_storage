@echo off
PUSHD ".."
@REM poetry env info -p
@REM echo "\Scripts\activate"
poetry export --without-hashes > requirements.txt
POPD