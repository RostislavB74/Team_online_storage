#!/bin/bash
#

export PROJECT_PATH="project_1444/"


_USER=appuser
_GROUP=appgroup
_IMAGES_DIR="/app/${PROJECT_PATH}uploads/images"
_STATIC_DIR="/app/${PROJECT_PATH}static"

TIMEOUT=${DB_WAIT_TIMEOUT:-20}
SLEEP=${DB_WAIT_SLEEP_TIME:-1}


function _check_code(){
  echo "Code verification starting..."
  if ! ruff check "/app/${PROJECT_PATH}"; then
    echo "Code verification failed - exit"
    exit 1
  fi
}

function _create_superuser_and_seeds(){
    if [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
        echo "Creating superuser..."
        python ${PROJECT_PATH}manage.py createsuperuser --username "$DJANGO_SUPERUSER_EMAIL" \
          --email "$DJANGO_SUPERUSER_EMAIL" --noinput || {
        echo "Superuser already created, skip load seeds"
        return 1
      }
    fi

    echo "Creating demo users..."
    python ${PROJECT_PATH}manage.py add_users

    echo "Running seed loader..."
    bash /app/commands/initialize_seeds.sh --no-input
}

function _make_migrations(){
  python ${PROJECT_PATH}manage.py makemigrations && \
  python ${PROJECT_PATH}manage.py migrate
}

function _make_collect_static(){
  python ${PROJECT_PATH}manage.py collectstatic --noinput
}

function _start_server(){
 # if [ ! -d /app/src/static/vendor ]; then exec su -c "python src/manage.py collectstatic --no-input" appuser; fi
 # exec su -c "gunicorn --chdir src --bind 0.0.0.0:8000 --workers=1 --worker-class=gthread --threads=4 config.wsgi:application" appuser
 # exec su -c "python src/manage.py runserver 0.0.0.0:8000" appuser
 # python src/manage.py runserver 0.0.0.0:8000

#  if [ -f "/app/build_info.env" ]; then
#   # add additional runtime environment about BUILD_INFO
#   source /app/build_info.env
#  fi
#  echo BRANCH_INFO="${BRANCH_INFO:-'undefined'} generated at ${GENERATED_AT}"

  if [ "${DEPLOY_MODE}" == "PROD" ] ;then
    echo "@ PRODUCTION MODE"
    python ${PROJECT_PATH}manage.py runserver 0.0.0.0:8000 --noreload --insecure --no-color
    # gunicorn --chdir src --bind 0.0.0.0:8000 --workers=1 --worker-class=gthread --threads=4 config.wsgi:application
  fi
  if [ "${DEPLOY_MODE}" == "DEV"  ];then
    echo "@ DEV MODE"
    python ${PROJECT_PATH}manage.py runserver --noreload --insecure  0.0.0.0:8000
  fi
  echo "Exit DEPLOY_MODE: ${DEPLOY_MODE}"
}

function _change_folder_permissions(){
  FOLDERS="${_IMAGES_DIR}"
  for folder in ${FOLDERS}; do
    echo " Change permissions for ${folder}"
    if [ ! -d "${folder}" ]; then mkdir -p "${folder}"; fi
    chown -R "${_USER}":"${_GROUP}" "${folder}"
  done
}

function _link_migrations(){
   bash /app/commands/link_migrations.sh
}


#### Main
#_check_code
_link_migrations && \
_make_migrations
_create_superuser_and_seeds
_change_folder_permissions
_make_collect_static
_start_server
