@echo off
PUSHD ".."
echo .
echo Starting generating requirements.txt
poetry export --without-hashes --with deploy > requirements.txt
POPD
