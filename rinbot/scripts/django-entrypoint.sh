#!/bin/bash
set -e

python manage.py makemigrations
python manage.py migrate

if [ "$BOT_RUN_WITH_DJANGO" = "True" ]; then
    python manage.py runserver --noreload 0.0.0.0:8000
else
    python manage.py runserver 0.0.0.0:8000
fi
