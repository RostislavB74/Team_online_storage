#!/bin/bash

PROJECT_PATH=${PROJECT_PATH:-"project_1444/"}

echo "Linking migrations to volume..."

SRC_DIR="/app/${PROJECT_PATH}"
TARGET_DIR="/app/data/migrations"

mkdir -p "$TARGET_DIR"

find "$SRC_DIR" \( -type d -o -type l \) -name "migrations" ! -path "*/__pycache__/*" | while read -r SRC_MIG_DIR; do
  REL_PATH="${SRC_MIG_DIR#$SRC_DIR/}"       # e.g., "myapp/migrations"
  APP_NAME=$(basename "$(dirname "$SRC_MIG_DIR")")  # e.g., "myapp"
  APP_SRC_PATH="$(dirname "$SRC_MIG_DIR")"
  TARGET_APP_MIG_DIR="$TARGET_DIR/$APP_NAME"

  if [ -d "$TARGET_APP_MIG_DIR" ] && ls "$TARGET_APP_MIG_DIR"/*.py >/dev/null 2>&1; then
    echo "Detected existing migrations in volume for: $APP_NAME"

    # Always remove and re-link to ensure it's fresh
    rm -rf "$SRC_MIG_DIR"
    ln -s "$TARGET_APP_MIG_DIR" "$SRC_MIG_DIR"
    echo "Linked: $SRC_MIG_DIR -> $TARGET_APP_MIG_DIR"
    continue
  fi


  # Migration not yet moved — move and link
  echo "Moving $SRC_MIG_DIR → $TARGET_APP_MIG_DIR"
  mkdir -p "$TARGET_APP_MIG_DIR"
  mv "$SRC_MIG_DIR"/* "$TARGET_APP_MIG_DIR"/ 2>/dev/null || true
  rm -rf "$SRC_MIG_DIR"

  ln -s "$TARGET_APP_MIG_DIR" "$SRC_MIG_DIR"
  echo "Linked: $SRC_MIG_DIR → $TARGET_APP_MIG_DIR"
done
