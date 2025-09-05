# Use an official Python runtime as a parent image
FROM python:3.10-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Copy Celery worker entrypoint and make it executable
COPY deployment/celery_worker_entrypoint.sh /app/celery_worker_entrypoint.sh
RUN chmod +x /app/celery_worker_entrypoint.sh

# ENTRYPOINT and CMD will be defined in docker-compose.yml for each service
