-- Revert initial schema tracking

BEGIN;

-- Drop audit table first due to foreign key constraint
DROP TABLE IF EXISTS schema_audit;

-- Drop migration tracking table
DROP TABLE IF EXISTS schema_migrations;

COMMIT;
