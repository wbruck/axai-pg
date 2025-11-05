# Schema SQL Files - DEPRECATED

⚠️ **These SQL files are deprecated and kept only for reference purposes.**

## Migration to SQLAlchemy-based Schema

As of the latest version, `axai-pg` uses SQLAlchemy models as the single source of truth for schema definition. The database schema is now created programmatically using `Base.metadata.create_all()` combined with PostgreSQL-specific DDL via `PostgreSQLSchemaBuilder`.

### Why the Change?

**Problems with dual maintenance:**
- SQL files and SQLAlchemy models were duplicates
- Risk of schema drift between SQL and Python
- Difficult to keep both in sync
- More maintenance overhead

**Benefits of SQLAlchemy-first approach:**
- Single source of truth (Python models)
- Type safety and IDE support
- Automatic schema generation
- Better testing capabilities
- Foundation for Alembic migrations

### How Schema is Now Created

The schema is created using:

```python
from axai_pg.utils import PostgreSQLSchemaBuilder
from axai_pg.data.config.database import Base

# Create complete schema with all PostgreSQL features
PostgreSQLSchemaBuilder.build_complete_schema(engine)
```

This:
1. Creates PostgreSQL extensions (uuid-ossp)
2. Creates custom functions (update_modified_column trigger)
3. Creates tables from SQLAlchemy models (`Base.metadata.create_all`)
4. Creates triggers for automatic timestamp updates
5. Adds table comments
6. Creates performance indexes

### For Reference Only

The `schema.sql` file in this directory is kept only as:
- Historical reference
- Documentation of the original design
- Comparison tool to verify SQLAlchemy models match original intent

**Do not use these SQL files for new deployments or development.**

### Migration Guide

If you were using SQL files directly:

**Old approach:**
```bash
psql -f sql/schema/schema.sql
```

**New approach:**
```python
from axai_pg.utils import DatabaseInitializer, DatabaseInitializerConfig
from axai_pg.data.config.database import PostgresConnectionConfig

config = DatabaseInitializerConfig(
    connection_config=PostgresConnectionConfig.from_env(),
    auto_create_db=True
)

db_init = DatabaseInitializer(config)
db_init.setup_database()  # Uses SQLAlchemy by default
```

Or for backward compatibility (not recommended):
```python
db_init.apply_schema(use_sqlalchemy=False)  # Falls back to SQL file
```

### Future: Alembic Migrations

For production schema changes, consider setting up Alembic migrations:
- Version-controlled schema changes
- Up/down migration support
- Automatic migration generation from model changes
- Production-ready rollback capabilities

See the documentation for migrating to Alembic-based schema management.

---

**Last Updated:** 2025-01-04
**Deprecated Since:** v0.2.0
