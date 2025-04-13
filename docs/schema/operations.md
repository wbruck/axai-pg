# PostgreSQL Operations Guide

## Indexing Strategy

### Core Document Access
```sql
-- Document lookup optimization
CREATE INDEX idx_documents_owner ON documents(owner_id);
CREATE INDEX idx_documents_organization ON documents(org_id);
CREATE INDEX idx_documents_type_status ON documents(document_type, status);
CREATE INDEX idx_documents_created ON documents(created_at);

-- Full-text search capability
CREATE INDEX idx_documents_title_tsvector ON documents USING GIN (to_tsvector('english', title));
CREATE INDEX idx_documents_content_tsvector ON documents USING GIN (to_tsvector('english', content));
```

### Summary Access
```sql
CREATE INDEX idx_summaries_document ON summaries(document_id);
CREATE INDEX idx_summaries_tool_agent ON summaries(tool_agent);
```

### Graph and Relationship Access
```sql
CREATE INDEX idx_graph_nodes_document ON graph_nodes(document_id) WHERE document_id IS NOT NULL;
CREATE INDEX idx_graph_relationships_source ON graph_relationships(source_node_id);
CREATE INDEX idx_graph_relationships_target ON graph_relationships(target_node_id);
CREATE INDEX idx_graph_relationships_type ON graph_relationships(relationship_type);
```

### Topic and Cluster Access
```sql
CREATE INDEX idx_document_topics_document ON document_topics(document_id);
CREATE INDEX idx_document_topics_topic ON document_topics(topic_id);
CREATE INDEX idx_document_topics_relevance ON document_topics(relevance_score DESC);
```

## Performance Optimization

### Query Optimization Guidelines

1. **Organization-Based Filtering**
   - Always include `org_id` in queries where possible
   - Use organization-based partitioning for large deployments
   ```sql
   SELECT *
   FROM documents
   WHERE org_id = $1
   AND created_at >= NOW() - INTERVAL '1 month'
   ORDER BY created_at DESC;
   ```

2. **Full-Text Search**
   - Use GIN indexes for text search operations
   - Consider cost of ranking in large result sets
   ```sql
   SELECT id, title, ts_rank(to_tsvector('english', content), query) as rank
   FROM documents
   WHERE to_tsvector('english', content) @@ plainto_tsquery('english', $1)
   ORDER BY rank DESC
   LIMIT 20;
   ```

3. **Batch Operations**
   - Use COPY for bulk data loading
   - Implement batch processing for large operations
   ```sql
   -- Example bulk insert using COPY
   COPY documents(title, content, owner_id, org_id, document_type)
   FROM '/path/to/data.csv' WITH (FORMAT csv, HEADER true);
   ```

### Connection Management

1. **Connection Pooling**
   ```
   # postgresql.conf settings
   max_connections = 100
   shared_buffers = 1GB
   work_mem = 10MB
   maintenance_work_mem = 256MB
   ```

2. **Application Settings**
   - Pool size: 5-10 connections per service
   - Statement timeout: 30 seconds
   - Idle timeout: 10 minutes

## Maintenance Procedures

### Regular Maintenance

1. **Statistics Updates**
   ```sql
   -- Update statistics
   ANALYZE documents;
   ANALYZE summaries;
   ANALYZE graph_nodes;
   ANALYZE graph_relationships;
   ```

2. **Index Maintenance**
   ```sql
   -- Rebuild indexes
   REINDEX TABLE documents;
   REINDEX TABLE summaries;
   ```

3. **Table Maintenance**
   ```sql
   -- Remove bloat
   VACUUM FULL documents;
   VACUUM FULL summaries;
   ```

### Monitoring Queries

1. **Index Usage**
   ```sql
   SELECT 
     schemaname,
     tablename,
     indexname,
     idx_scan,
     idx_tup_read,
     idx_tup_fetch
   FROM pg_stat_user_indexes
   ORDER BY idx_scan DESC;
   ```

2. **Table Statistics**
   ```sql
   SELECT 
     relname,
     n_live_tup,
     n_dead_tup,
     last_vacuum,
     last_autovacuum
   FROM pg_stat_user_tables;
   ```

3. **Query Performance**
   ```sql
   SELECT 
     query,
     calls,
     total_time,
     mean_time,
     rows
   FROM pg_stat_statements
   ORDER BY total_time DESC
   LIMIT 10;
   ```

## Backup and Recovery

### Backup Strategy

1. **Physical Backups**
   ```bash
   # Full backup
   pg_basebackup -D /backup/path -Ft -z -P
   ```

2. **Logical Backups**
   ```bash
   # Full database backup
   pg_dump dbname > backup.sql
   
   # Schema-only backup
   pg_dump -s dbname > schema.sql
   ```

3. **Point-in-Time Recovery Setup**
   ```
   # postgresql.conf
   wal_level = replica
   archive_mode = on
   archive_command = 'test ! -f /archive/%f && cp %p /archive/%f'
   ```

### Recovery Procedures

1. **Full Database Recovery**
   ```bash
   # Stop PostgreSQL
   pg_ctl stop
   
   # Restore base backup
   pg_basebackup -D $PGDATA -Ft -z -P
   
   # Start PostgreSQL
   pg_ctl start
   ```

2. **Point-in-Time Recovery**
   ```
   # recovery.conf
   restore_command = 'cp /archive/%f %p'
   recovery_target_time = '2023-12-31 23:59:59'
   ```

## Monitoring Guidelines

### Key Metrics

1. **Performance Metrics**
   - Query execution time
   - Index usage rates
   - Cache hit ratios
   - Connection counts

2. **Storage Metrics**
   - Table and index sizes
   - WAL generation rate
   - Free space monitoring
   - Bloat levels

3. **Error Monitoring**
   - Failed queries
   - Lock timeouts
   - Deadlocks
   - Connection failures

### Alert Thresholds

1. **Response Time**
   - Query time > 1 second
   - Connection time > 100ms
   - Transaction time > 5 seconds

2. **Resource Usage**
   - CPU usage > 80%
   - Memory usage > 90%
   - Disk usage > 85%
   - Connection usage > 80%

## Scaling Guidelines

### Vertical Scaling

1. **Memory Settings**
   ```
   shared_buffers = 25% of RAM
   effective_cache_size = 75% of RAM
   maintenance_work_mem = 256MB
   work_mem = 10MB per connection
   ```

2. **CPU Settings**
   ```
   max_worker_processes = 8
   max_parallel_workers_per_gather = 4
   max_parallel_workers = 8
   ```

### Horizontal Scaling

1. **Read Replicas**
   - Set up streaming replication
   - Configure read-only queries
   - Implement connection routing

2. **Partitioning**
   - Consider organization-based partitioning
   - Implement time-based partitioning for historical data
   - Use declarative partitioning
