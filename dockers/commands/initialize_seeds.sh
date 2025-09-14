#!/bin/bash

PROJECT_PATH=${PROJECT_PATH:-"project_1444/"}

echo "Initialize seeds"

# User confirmation unless --no-input is passed
if [ "$1" != "--no-input" ]; then
  read -p "You are sure? Old data will be overloaded (y/n): " CONFIRM
  if [ "$CONFIRM" != "y" ]; then
    echo "Aborted."
    exit 1
  fi
fi

SRC_DIR="/app/${PROJECT_PATH}"

# Collect all seed JSON files, sort by base filename (0001_*.json)
mapfile -t SEED_FILES < <(find "$SRC_DIR" -type f -path "*/seed/*.json" | sort -t/ -k1 | awk -F/ '{print $0 "|" $NF}' | sort -t'|' -k2 | cut -d'|' -f1)

echo "Loading all seed files in global order:"
for FILE in "${SEED_FILES[@]}"; do
  APP_PATH=$(dirname "$(dirname "$FILE")")     # e.g., /app/src/users
  APP_NAME=$(basename "$APP_PATH")             # e.g., users
  echo "  - Loading [$APP_NAME] $FILE"
  python "${SRC_DIR}/manage.py" loaddata --app "$APP_NAME" "$FILE"
done