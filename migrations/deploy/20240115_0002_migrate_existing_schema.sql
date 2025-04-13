-- Deploy existing schema migration

BEGIN;

-- Log the migration of existing schema
INSERT INTO schema_migrations (
    version,
    description,
    installed_on
) VALUES (
    '20240115_0002_migrate_existing_schema',
    'Migrate existing schema into versioning system',
    CURRENT_TIMESTAMP
);

-- Log each major component of the existing schema
INSERT INTO schema_audit (migration_id, operation_type, object_type, object_name, description)
VALUES 
    ('20240115_0002_migrate_existing_schema', 'REGISTER', 'TABLE', 'organizations', 'Core organization table'),
    ('20240115_0002_migrate_existing_schema', 'REGISTER', 'TABLE', 'users', 'User management table'),
    ('20240115_0002_migrate_existing_schema', 'REGISTER', 'TABLE', 'documents', 'Document storage table'),
    ('20240115_0002_migrate_existing_schema', 'REGISTER', 'TABLE', 'document_versions', 'Document version history'),
    ('20240115_0002_migrate_existing_schema', 'REGISTER', 'TABLE', 'summaries', 'Document summaries'),
    ('20240115_0002_migrate_existing_schema', 'REGISTER', 'TABLE', 'graph_nodes', 'Graph structure nodes'),
    ('20240115_0002_migrate_existing_schema', 'REGISTER', 'TABLE', 'graph_relationships', 'Graph relationships'),
    ('20240115_0002_migrate_existing_schema', 'REGISTER', 'TABLE', 'topics', 'Document topics'),
    ('20240115_0002_migrate_existing_schema', 'REGISTER', 'TABLE', 'document_topics', 'Document-topic associations'),
    ('20240115_0002_migrate_existing_schema', 'REGISTER', 'TABLE', 'document_clusters', 'Document clusters'),
    ('20240115_0002_migrate_existing_schema', 'REGISTER', 'TABLE', 'document_cluster_members', 'Cluster memberships');

COMMIT;
