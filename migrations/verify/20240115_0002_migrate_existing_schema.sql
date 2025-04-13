-- Verify existing schema migration

BEGIN;

-- Verify migration is recorded
SELECT 1/COUNT(*) FROM schema_migrations 
WHERE version = '20240115_0002_migrate_existing_schema';

-- Verify all major tables are recorded in audit
SELECT 1/COUNT(*) FROM schema_audit 
WHERE migration_id = '20240115_0002_migrate_existing_schema'
AND object_type = 'TABLE'
AND object_name IN (
    'organizations',
    'users',
    'documents',
    'document_versions',
    'summaries',
    'graph_nodes',
    'graph_relationships',
    'topics',
    'document_topics',
    'document_clusters',
    'document_cluster_members'
);

ROLLBACK;
