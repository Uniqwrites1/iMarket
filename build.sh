#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Force SQLite during build to avoid PostgreSQL issues
export DJANGO_SETTINGS_MODULE=iMarket.settings
export DATABASE_URL=""
export RENDER_BUILD=true

# Collect static files (using SQLite fallback)
python manage.py collectstatic --no-input --clear

# Remove build flag
unset RENDER_BUILD

# Run migrations only if we have a real DATABASE_URL
if [ -n "$DATABASE_URL_EXTERNAL" ]; then
    export DATABASE_URL=$DATABASE_URL_EXTERNAL
    python manage.py migrate
else
    echo "No external database URL provided, skipping migrations"
fi
