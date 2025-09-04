#!/bin/bash
set -e

# Wait for the database to be ready
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  echo "Waiting for database..."
  sleep 2
done

# Initialize Alembic if migrations folder does not exist
if [ ! -d "migrations" ]; then
  echo "Initializing Alembic..."
  alembic init migrations
fi

# Always run migrations
alembic upgrade head

# Start the main application (pass all arguments)
exec "$@"
