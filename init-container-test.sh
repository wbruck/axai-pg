#!/bin/bash

# Exit on error
set -e

echo "Starting test environment setup..."

# Validate environment variables
echo "Validating environment variables..."
expected_vars=(
    "POSTGRES_USER=test_user"
    "POSTGRES_PASSWORD=test_password"
    "POSTGRES_DB=test_db"
    "POSTGRES_HOST=postgres"
)

for expected in "${expected_vars[@]}"; do
    var_name="${expected%=*}"
    expected_value="${expected#*=}"
    actual_value="${!var_name}"
    
    if [ "$actual_value" != "$expected_value" ]; then
        echo "ERROR: Environment variable $var_name is '$actual_value', expected '$expected_value'"
        exit 1
    fi
    echo "✓ $var_name is set correctly"
done

# Wait for PostgreSQL to be ready with exponential backoff
echo "Waiting for PostgreSQL to be ready..."
MAX_ATTEMPTS=5
INITIAL_WAIT=1
MAX_WAIT=30
attempt=1
wait_time=$INITIAL_WAIT

while [ $attempt -le $MAX_ATTEMPTS ]; do
    echo "Attempt $attempt of $MAX_ATTEMPTS..."
    
    if command -v pg_isready >/dev/null 2>&1; then
        echo "Testing PostgreSQL connection..."
        pg_isready -h postgres -U test_user -d test_db
        result=$?
        echo "pg_isready exit code: $result"
    else
        echo "pg_isready command not found"
        result=1
    fi
    
    if [ $result -eq 0 ]; then
        echo "PostgreSQL is ready!"
        break
    fi
    
    if [ $attempt -eq $MAX_ATTEMPTS ]; then
        echo "PostgreSQL is still not ready after $MAX_ATTEMPTS attempts. Giving up."
        exit 1
    fi
    
    echo "PostgreSQL is unavailable - sleeping for $wait_time seconds"
    sleep $wait_time
    
    wait_time=$((wait_time * 2))
    if [ $wait_time -gt $MAX_WAIT ]; then
        wait_time=$MAX_WAIT
    fi
    
    attempt=$((attempt + 1))
done

# Drop and recreate the database
echo "Dropping and recreating database..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h postgres -U test_user -d postgres -c "DROP DATABASE IF EXISTS test_db;"
PGPASSWORD=$POSTGRES_PASSWORD psql -h postgres -U test_user -d postgres -c "CREATE DATABASE test_db;"

# Apply database schema
echo "Applying database schema..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h postgres -U test_user -d test_db < /app/sql/schema/schema.sql

# Install the local package in development mode
echo "Installing axai-pg package..."
pip install -e .

# Run the tests
echo "Running tests..."
pytest tests/ -v --cov=axai_pg --cov-report=term-missing

echo "Test environment setup complete!" 