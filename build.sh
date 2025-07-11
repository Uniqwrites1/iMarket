#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files (disable database operations)
python manage.py collectstatic --no-input --clear

# Run migrations (only if DATABASE_URL is set)
if [ -n "$DATABASE_URL" ]; then
    python manage.py migrate
else
    echo "DATABASE_URL not set, skipping migrations"
fi
