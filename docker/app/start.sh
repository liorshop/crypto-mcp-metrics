#!/bin/bash

# Wait for PostgreSQL
while ! nc -z postgres 5432; do
    echo "Waiting for PostgreSQL..."
    sleep 1
done

# Wait for Redis
while ! nc -z redis 6379; do
    echo "Waiting for Redis..."
    sleep 1
done

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port 8000