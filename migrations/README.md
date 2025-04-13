# Database Migrations

This directory contains database migrations for the document management system. The migrations follow a sequential versioning scheme and are managed using Sqitch, a database change management system that offers precise control over PostgreSQL migrations.

## Migration Naming Convention

Migrations follow this format:
`YYYYMMDD_NNNN_description.sql`
- YYYYMMDD: Date the migration was created
- NNNN: Sequential number for that day (0001, 0002, etc.)
- description: Brief description using underscores

Example: `20240115_0001_add_document_tags.sql`

## Migration Types

1. **Schema Changes** (`schema/`):
   - Table creation/modification
   - Index changes
   - Constraint changes
   
2. **Data Migrations** (`data/`):
   - Data transformations
   - Backfills
   - Cleanup operations

## Migration Process

### Development
1. Create new migration:
   ```bash
   sqitch add YYYYMMDD_NNNN_description -n "Description of changes"
   ```

2. Implement migration files:
   - `migrations/deploy/YYYYMMDD_NNNN_description.sql` (forward migration)
   - `migrations/revert/YYYYMMDD_NNNN_description.sql` (rollback)
   - `migrations/verify/YYYYMMDD_NNNN_description.sql` (verification)

3. Test locally:
   ```bash
   sqitch deploy db:pg://localhost/testdb --verify
   sqitch revert db:pg://localhost/testdb -y 1
   ```

### Review Process
1. Create PR with:
   - Migration files
   - Test cases
   - Documentation updates
   - Performance impact analysis
   
2. Required approvals:
   - Database admin review
   - Application developer review
   - Product owner sign-off for data migrations

### Deployment
1. Schedule maintenance window if needed
2. Backup database
3. Deploy migration to staging
4. Verify staging deployment
5. Deploy to production during window
6. Verify production deployment

## Safety Measures

1. **All migrations must be reversible**
2. **Explicit verification steps required**
3. **Large data migrations must be batched**
4. **Maintain backward compatibility**
5. **Monitor performance during migration**

## Monitoring

During migration execution:
- Transaction logs
- Query performance
- Lock contention
- Application errors
- Replication lag

## Emergency Procedures

If issues occur during migration:
1. Execute rollback procedure
2. Verify system stability
3. Investigate root cause
4. Update migration plan
5. Reschedule with fixes

## Version History

Version history is tracked in the `schema_versions` table and through Sqitch's internal tracking.
