#!/bin/sh
set -e

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Configuring Nginx..."
nginx -t

echo "Starting Nginx..."
nginx -g "daemon off;" &

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --timeout 120
