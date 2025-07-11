#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Use SQLite for static file collection (no DB connection needed)
export DATABASE_URL_TEMP=$DATABASE_URL
unset DATABASE_URL

# Collect static files
python manage.py collectstatic --no-input --clear

# Restore DATABASE_URL and run migrations
export DATABASE_URL=$DATABASE_URL_TEMP

# Run migrations (only if DATABASE_URL is set)
if [ -n "$DATABASE_URL" ]; then
    python manage.py migrate
else
    echo "DATABASE_URL not set, skipping migrations"
fi
