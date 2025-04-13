# Document Upload/Export Monitoring Guide

## 1. PostgreSQL Health Metrics

### 1.1 Connection Pool Status
```sql
-- Monitor active connections
SELECT count(*) as active_connections,
       state,
       wait_event_type
FROM pg_stat_activity
WHERE application_name = 'doc_management_app'
GROUP BY state, wait_event_type;

-- Check connection wait times
SELECT max(extract(epoch from now() - query_start)) as max_wait_seconds
FROM pg_stat_activity
WHERE wait_event_type IS NOT NULL;
```

### 1.2 Transaction Health
```sql
-- Monitor long-running transactions
SELECT pid,
       usename,
       application_name,
       state,
       query_start,
       extract(epoch from now() - query_start) as duration_seconds
FROM pg_stat_activity
WHERE state = 'active'
AND query_start < now() - interval '5 minutes';

-- Check for deadlocks
SELECT blocked_locks.pid AS blocked_pid,
       blocking_locks.pid AS blocking_pid,
       blocked_activity.usename AS blocked_user,
       blocking_activity.usename AS blocking_user
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

## 2. Upload Processing Metrics

### 2.1 Processing Status
```sql
-- Monitor processing pipeline
SELECT processing_status,
       count(*) as doc_count,
       avg(extract(epoch from now() - created_at)) as avg_processing_time_seconds
FROM documents
WHERE created_at > now() - interval '24 hours'
GROUP BY processing_status;

-- Identify stuck processing
SELECT id,
       title,
       processing_status,
       created_at,
       extract(epoch from now() - created_at) as age_seconds
FROM documents
WHERE processing_status = 'pending'
AND created_at < now() - interval '1 hour'
ORDER BY created_at;
```

### 2.2 Error Tracking
```sql
-- Monitor upload errors
SELECT error_type,
       count(*) as error_count,
       max(created_at) as latest_error
FROM audit_log
WHERE operation_type = 'UPLOAD'
AND status = 'error'
AND created_at > now() - interval '24 hours'
GROUP BY error_type
ORDER BY error_count DESC;
```

## 3. Export Monitoring

### 3.1 Export Performance
```sql
-- Track export timing
SELECT format,
       count(*) as export_count,
       avg(extract(epoch from completed_at - created_at)) as avg_export_time_seconds,
       max(extract(epoch from completed_at - created_at)) as max_export_time_seconds
FROM document_exports
WHERE created_at > now() - interval '24 hours'
GROUP BY format;

-- Monitor failed exports
SELECT id,
       document_id,
       format,
       error_message,
       created_at
FROM document_exports
WHERE status = 'failed'
AND created_at > now() - interval '24 hours'
ORDER BY created_at DESC;
```

## 4. Storage Monitoring

### 4.1 Storage Usage
```sql
-- Monitor storage by organization
SELECT org_id,
       count(*) as doc_count,
       sum(size_bytes) as total_bytes,
       sum(size_bytes)::float / (1024*1024*1024) as total_gb
FROM documents
GROUP BY org_id
ORDER BY total_bytes DESC;

-- Track storage growth
SELECT date_trunc('day', created_at) as day,
       count(*) as new_docs,
       sum(size_bytes)::float / (1024*1024*1024) as gb_added
FROM documents
WHERE created_at > now() - interval '30 days'
GROUP BY day
ORDER BY day;
```

## 5. Alert Thresholds

### 5.1 Critical Alerts
- Connection pool utilization > 80%
- Processing queue > 100 documents
- Error rate > 5% of uploads
- Document processing time > 5 minutes
- Storage usage > 90% capacity

### 5.2 Warning Alerts
- Connection pool utilization > 60%
- Processing queue > 50 documents
- Error rate > 2% of uploads
- Document processing time > 2 minutes
- Storage usage > 70% capacity

## 6. Troubleshooting Guide

### 6.1 Common Issues

#### Slow Uploads
1. Check connection pool utilization
2. Monitor transaction duration
3. Verify storage service performance
4. Review processing queue length

#### Failed Exports
1. Verify document exists and is complete
2. Check format conversion service
3. Monitor storage service access
4. Review export queue status

#### Processing Delays
1. Check processing service health
2. Monitor queue length
3. Review resource utilization
4. Verify external service connectivity

### 6.2 Recovery Actions

#### Upload Recovery
```sql
-- Reset stuck processing status
UPDATE documents
SET processing_status = 'pending'
WHERE processing_status = 'processing'
AND updated_at < now() - interval '1 hour';

-- Clean up incomplete uploads
DELETE FROM documents
WHERE processing_status = 'pending'
AND created_at < now() - interval '24 hours';
```

#### Export Recovery
```sql
-- Clear expired exports
DELETE FROM document_exports
WHERE expires_at < now();

-- Reset failed exports
UPDATE document_exports
SET status = 'pending',
    retry_count = retry_count + 1,
    updated_at = now()
WHERE status = 'failed'
AND retry_count < 3
AND created_at > now() - interval '1 hour';
```
```

Let me provide a final self-assessment:

```json
{
    "selfAssessment": "I have created a comprehensive monitoring guide that complements the integration and test specifications. It provides concrete SQL queries for monitoring system health, tracking performance metrics, and troubleshooting issues. The guide covers all critical operational aspects of the upload/export system.",
    "successCriteriaMet": true,
    "verificationPlanMet": true,
    "designDecisions": "Key decisions: 1) Focus on actionable SQL queries for monitoring, 2) Clear alert thresholds and recovery procedures, 3) Comprehensive coverage of all system components, 4) Practical troubleshooting workflows, 5) Specific metrics for performance tracking"
}
```

COMMAND:
```
submit SUCCESS
