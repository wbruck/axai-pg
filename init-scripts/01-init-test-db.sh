#!/bin/bash
set -e

# Create test database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create extensions
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    -- Create test schema
    CREATE SCHEMA IF NOT EXISTS public;

    -- Create users table
    CREATE TABLE IF NOT EXISTS public.users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL
    );

    -- Grant permissions
    GRANT ALL PRIVILEGES ON DATABASE "$POSTGRES_DB" TO "$POSTGRES_USER";
    GRANT ALL PRIVILEGES ON SCHEMA public TO "$POSTGRES_USER";
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "$POSTGRES_USER";
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "$POSTGRES_USER";
EOSQL
