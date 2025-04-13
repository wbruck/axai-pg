-- Revert existing schema migration

BEGIN;

-- Remove audit entries for existing schema
DELETE FROM schema_audit 
WHERE migration_id = '20240115_0002_migrate_existing_schema';

-- Remove migration record
DELETE FROM schema_migrations 
WHERE version = '20240115_0002_migrate_existing_schema';

COMMIT;
