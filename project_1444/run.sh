#!/usr/bin/env bash

gunicorn --bind "0.0.0.0:8000" "project_1444.wsgi:application"