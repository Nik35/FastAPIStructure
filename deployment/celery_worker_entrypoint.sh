#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting Celery worker..."

# Run Celery worker
# -A app.core.celery_app: points to your Celery application instance
# worker: specifies that you're starting a worker
# -l info: sets the log level to info
# -c ${CELERY_WORKER_CONCURRENCY:-4}: sets concurrency, defaults to 4 if CELERY_WORKER_CONCURRENCY env var is not set
# -Q ${CELERY_QUEUE:-celery}: specifies the queue(s) to consume from, defaults to 'celery'
# --autoscale=10,1: autoscale from 1 to 10 processes based on load (optional)
# --without-gossip --without-mingle --without-heartbeat: reduce overhead for simple workers (optional)

celery -A app.core.celery_app worker -l "${CELERY_WORKER_LOG_LEVEL:-INFO}" \
       -c "${CELERY_WORKER_CONCURRENCY:-4}" \
       -Q "${CELERY_QUEUE:-celery}"
