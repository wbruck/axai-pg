-- Verify initial schema tracking

BEGIN;

-- Verify tables exist with correct structure
SELECT version, installed_by, description, installed_on, success, execution_time
FROM schema_migrations
WHERE FALSE;

SELECT id, migration_id, operation_type, object_type, object_name, 
       description, performed_at, performed_by, sql_statement
FROM schema_audit
WHERE FALSE;

-- Verify indexes exist
SELECT 1/COUNT(*) FROM pg_indexes 
WHERE tablename = 'schema_migrations' 
  AND indexname = 'idx_schema_migrations_installed';

SELECT 1/COUNT(*) FROM pg_indexes 
WHERE tablename = 'schema_audit' 
  AND indexname IN ('idx_schema_audit_migration', 'idx_schema_audit_performed');

ROLLBACK;
