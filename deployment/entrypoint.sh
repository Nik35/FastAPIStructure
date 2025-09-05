#!/bin/bash
set -e

# Wait for the database to be ready
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  echo "Waiting for database..."
  sleep 2
done


# Initialize Alembic if app/models/migrations folder does not exist
if [ ! -d "app/models/migrations" ]; then
  echo "Initializing Alembic in app/models/migrations..."
  alembic -c alembic.ini init app/models/migrations
fi

# Always run migrations
alembic -c alembic.ini upgrade head

# Start the main application (pass all arguments)
exec "$@"
