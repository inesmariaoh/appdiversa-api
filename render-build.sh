#!/usr/bin/env bash
# Script de compilacion para Render (build command).
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
