# PostgreSQL Schema Migration Guide

## Overview

This document details the process and best practices for managing PostgreSQL schema migrations in the document management system using Sqitch.

## Migration Process

### 1. Development Phase

#### Creating a New Migration
```bash
# Create a new migration
sqitch add YYYYMMDD_NNNN_description -n "Description of changes"
```

Each migration requires three files:
- `deploy/*.sql`: Forward migration script
- `revert/*.sql`: Rollback script
- `verify/*.sql`: Verification script

#### Migration Guidelines

1. **Naming Convention**
   - Format: `YYYYMMDD_NNNN_description`
   - Example: `20240115_0001_add_document_tags`

2. **Content Requirements**
   - BEGIN/COMMIT transaction blocks
   - Comprehensive comments
   - Idempotent operations where possible
   - Explicit schema references

3. **Safety Measures**
   - Include transaction blocks
   - Add verification steps
   - Implement rollback logic
   - Handle existing data
   - Consider performance impact

### 2. Testing Phase

```bash
# Test deployment
sqitch deploy db:pg://localhost/testdb --verify

# Test revert
sqitch revert db:pg://localhost/testdb -y 1

# Verify state
sqitch verify db:pg://localhost/testdb
```

#### Validation Steps
1. Deploy migration to test database
2. Verify schema changes
3. Test application functionality
4. Measure performance impact
5. Test rollback procedure
6. Verify data integrity

### 3. Review Process

Required Documentation:
1. Migration scripts
2. Test results
3. Performance analysis
4. Rollback procedure
5. Deployment timeline

Approval Requirements:
- Database administrator review
- Lead developer sign-off
- Product owner approval (for data migrations)

### 4. Deployment Phase

#### Pre-deployment
1. Schedule maintenance window if needed
2. Notify stakeholders
3. Backup database
4. Verify backup

#### Deployment Steps
1. Deploy to staging environment
2. Verify staging deployment
3. Run application tests
4. Deploy to production
5. Verify production deployment
6. Monitor system health

#### Post-deployment
1. Verify application functionality
2. Monitor performance metrics
3. Check error logs
4. Update documentation
5. Close migration ticket

### 5. Emergency Procedures

If issues occur:
1. Execute rollback procedure
2. Verify system stability
3. Notify stakeholders
4. Document incident
5. Update migration plan

## Best Practices

### Schema Changes

1. **Backward Compatibility**
   - Maintain compatibility with existing code
   - Use temporary duplicates for large changes
   - Coordinate with application deployments

2. **Performance Considerations**
   - Use concurrent index creation when possible
   - Batch large data migrations
   - Monitor lock contention
   - Consider maintenance windows for heavy operations

3. **Data Safety**
   - Always backup before migration
   - Use transactions appropriately
   - Validate data before and after changes
   - Keep audit trails of changes

### Common Patterns

1. **Adding Columns**
```sql
-- Deploy
ALTER TABLE table_name 
ADD COLUMN column_name data_type [constraints];

-- Verify
SELECT column_name FROM table_name WHERE FALSE;

-- Revert
ALTER TABLE table_name 
DROP COLUMN column_name;
```

2. **Modifying Constraints**
```sql
-- Deploy
ALTER TABLE table_name 
ADD CONSTRAINT constraint_name CHECK (condition);

-- Verify
SELECT constraint_name 
FROM information_schema.table_constraints 
WHERE table_name = 'table_name';

-- Revert
ALTER TABLE table_name 
DROP CONSTRAINT constraint_name;
```

3. **Creating Indexes**
```sql
-- Deploy
CREATE INDEX CONCURRENTLY idx_name 
ON table_name (column_name);

-- Verify
SELECT indexname FROM pg_indexes 
WHERE tablename = 'table_name' 
AND indexname = 'idx_name';

-- Revert
DROP INDEX CONCURRENTLY idx_name;
```

## Migration Tracking

Migrations are tracked in two tables:

1. `schema_migrations`: Core migration history
   - version
   - installed_by
   - description
   - installed_on
   - success
   - execution_time

2. `schema_audit`: Detailed change tracking
   - migration_id
   - operation_type
   - object_type
   - object_name
   - description
   - performed_at
   - performed_by
   - sql_statement

## Monitoring and Maintenance

Regular Tasks:
1. Review migration history
2. Clean up old migrations
3. Update documentation
4. Test recovery procedures
5. Audit access controls

## Support and Resources

- [Sqitch Documentation](https://sqitch.org/docs/)
- [PostgreSQL Alter Table](https://www.postgresql.org/docs/current/sql-altertable.html)
- [PostgreSQL Backup/Restore](https://www.postgresql.org/docs/current/backup.html)
