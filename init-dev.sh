#!/bin/bash

# Exit on error
set -e

echo "Starting development environment setup..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until docker exec axai-pg-test pg_isready -U test_user -d test_db; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done

echo "PostgreSQL is ready!"

# Apply database schema
echo "Applying database schema..."
docker exec -i axai-pg-test psql -U test_user -d test_db < sql/schema/schema.sql

# Install the local package in development mode
echo "Installing axai-pg package..."
pip install -e .

# Set environment variables for the sample data script
echo "Setting up environment variables..."
export POSTGRES_USER=test_user
export POSTGRES_PASSWORD=test_password
export POSTGRES_DB=test_db

# Run the sample data script
echo "Loading sample data..."
python add_sample_data.py

echo "Development environment setup complete!" 