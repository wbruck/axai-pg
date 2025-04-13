-- Deploy initial schema tracking

BEGIN;

-- Create schema_migrations table for Sqitch
CREATE TABLE schema_migrations (
    version TEXT PRIMARY KEY,
    installed_by TEXT NOT NULL DEFAULT CURRENT_USER,
    description TEXT NOT NULL,
    installed_on TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN NOT NULL DEFAULT TRUE,
    execution_time INTEGER NOT NULL DEFAULT 0
);

-- Create schema_audit for tracking detailed changes
CREATE TABLE schema_audit (
    id SERIAL PRIMARY KEY,
    migration_id TEXT NOT NULL REFERENCES schema_migrations(version),
    operation_type TEXT NOT NULL,
    object_type TEXT NOT NULL,
    object_name TEXT NOT NULL,
    description TEXT,
    performed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    performed_by TEXT NOT NULL DEFAULT CURRENT_USER,
    sql_statement TEXT
);

-- Create indexes
CREATE INDEX idx_schema_migrations_installed ON schema_migrations(installed_on);
CREATE INDEX idx_schema_audit_migration ON schema_audit(migration_id);
CREATE INDEX idx_schema_audit_performed ON schema_audit(performed_at DESC);

COMMIT;
