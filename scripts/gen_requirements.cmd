@echo off
PUSHD ".."
echo .
echo Starting generating requirements.txt
poetry export --without-hashes --with deploy --without dev > requirements.txt
poetry export --without-hashes --only dev > requirements-dev.txt
POPD
