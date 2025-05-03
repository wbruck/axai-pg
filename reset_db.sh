#!/bin/bash

# Exit on error
set -e

echo "Resetting database in Docker container..."

# Check if Docker container is running
if ! docker ps | grep -q axai-pg-test; then
    echo "Error: Docker container 'axai-pg-test' is not running"
    exit 1
fi

# Drop and recreate the database
echo "Dropping and recreating database..."
docker exec axai-pg-test psql -U test_user -d postgres -c "DROP DATABASE IF EXISTS test_db;"
docker exec axai-pg-test psql -U test_user -d postgres -c "CREATE DATABASE test_db;"

# Apply database schema
echo "Applying database schema..."
docker exec -i axai-pg-test psql -U test_user -d test_db < sql/schema/schema.sql

echo "Database reset complete!" 