# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AXAI PostgreSQL Models (`axai-pg`) is a Python package providing PostgreSQL database models and repository layer for a multi-tenant B2B document management system. The project was recently migrated from TypeScript to Python and uses SQLAlchemy 2.0 for database operations.

## Common Commands

### Setup and Installation
```bash
# Install dependencies (development mode)
pip install -e .

# Install with all development dependencies
pip install -e ".[dev]"
```

### Testing
```bash
# Start PostgreSQL test container
docker-compose -f docker-compose.standalone-test.yml up -d postgres

# Run all tests via script (recommended)
./run_tests.sh

# Run tests manually
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/integration/ -v --integration

# Run specific test file
pytest tests/integration/test_schema_creation.py -v --integration
pytest tests/integration/test_crud_operations.py -v --integration

# Run with coverage (if pytest-cov is installed)
pytest tests/integration/ -v --integration --cov=src --cov-report=html --cov-report=term-missing

# Clean up test containers
docker-compose -f docker-compose.standalone-test.yml down -v
```

### Database Management
Schema is created programmatically using `PostgreSQLSchemaBuilder`. See "SQLAlchemy-First Schema Management" section below for details.

```python
# Programmatically create/reset database
from axai_pg.utils import DatabaseInitializer, DatabaseInitializerConfig
from axai_pg.data.config.database import PostgresConnectionConfig

config = DatabaseInitializerConfig(
    connection_config=PostgresConnectionConfig.from_env(),
    auto_create_db=True
)

db_init = DatabaseInitializer(config)
db_init.setup_database()  # Creates schema using SQLAlchemy models
```

### Code Quality
```bash
# Format code with black
black src/ tests/

# Run linter
flake8 src/ tests/

# Type checking
mypy src/

# Run pre-commit hooks
pre-commit run --all-files

# Install pre-commit hooks
pre-commit install
```

### Development
```bash
# Start PostgreSQL database for local development
docker-compose up -d

# Build package
python -m build

# Install locally
pip install -e .
```

## Architecture Overview

### Core Components

#### 1. Database Layer (`src/axai_pg/data/`)
- **DatabaseManager**: Singleton managing database connections, connection pooling, and session lifecycle
- **Base declarative model**: SQLAlchemy declarative base for all models
- **Connection pooling**: Configured with pool_size, max_overflow, pool_timeout, pool_recycle
- **Session management**: Context manager pattern with automatic commit/rollback

#### 2. Models (`src/axai_pg/data/models/`)
Core domain models representing the schema:
- **Organization**: B2B tenant entities (multi-tenant isolation)
- **User**: Users belonging to organizations
- **Document**: Core document storage with versioning, ownership, and metadata
- **DocumentVersion**: Historical document versions with change tracking
- **Summary**: AI-generated document summaries with tool/agent attribution
- **Topic**: Topics extracted from document content
- **GraphNode**: Nodes in document relationship graph
- **GraphRelationship**: Edges connecting document nodes
- **DocumentTopic**: Many-to-many relationship between documents and topics

All models use UUID primary keys and include `created_at`/`updated_at` timestamps.

#### 3. Repository Pattern (`src/axai_pg/data/repositories/`)
Abstraction layer providing:
- **BaseRepository**: Generic CRUD operations, transaction management
- **DocumentRepository**: Document-specific queries (related documents, topic-based queries)
- **RepositoryFactory**: Singleton factory managing repository instances
- **CacheManager**: Query result caching with TTL and invalidation
- **Metrics decorators**: Automatic timing, error tracking, cache hit rate monitoring

Key patterns:
- Async/await throughout for consistency
- Transaction support with automatic rollback on errors
- TTL-based caching with configurable durations
- Session-per-request pattern

#### 4. Security Layer (`src/axai_pg/data/security/`)
- **Organization-level isolation**: Multi-tenant data separation
- **Query middleware**: Automatic filtering by organization context
- **Security manager**: Centralized security configuration
- **Repository security**: Access control at repository level

#### 5. Configuration (`src/axai_pg/data/config/`)
- **PostgresConnectionConfig**: Database connection parameters
- **PostgresPoolConfig**: Connection pool configuration
- **Environment-based config**: Support for loading from environment variables

### Multi-Tenant Architecture

The system implements B2B multi-tenancy with organization-level isolation:
- Every document and user belongs to an organization
- Query middleware automatically filters by org_id
- Foreign key constraints enforce data integrity
- Users can only access data within their organization

### Migration System

Uses Sqitch for database change management:
- **Deploy scripts**: Forward migrations (`migrations/deploy/`)
- **Revert scripts**: Rollback migrations (`migrations/revert/`)
- **Verify scripts**: Validation checks (`migrations/verify/`)

Naming convention: `YYYYMMDD_NNNN_description.sql`

All migrations must be:
- Reversible
- Tested in staging before production
- Documented with performance impact analysis
- Backward compatible when possible

### Testing Strategy

**SQLAlchemy-First Integration Testing:**

All tests use a real PostgreSQL database with no mocks. The schema is created programmatically from SQLAlchemy models using `PostgreSQLSchemaBuilder`, which:
1. Creates PostgreSQL extensions (uuid-ossp)
2. Creates custom trigger functions (auto-update timestamps)
3. Creates tables from SQLAlchemy models
4. Creates triggers for each table
5. Adds table comments
6. Creates performance indexes

**Test Structure:**
- **`tests/integration/`**: All tests (40 tests total: 39 passing, 1 skipped)
  - `test_schema_creation.py`: Schema validation (16 tests)
  - `test_schema_builder.py`: PostgreSQLSchemaBuilder functionality (10 tests)
  - `test_database_initializer.py`: Database lifecycle management (8 tests)
  - `test_crud_operations.py`: CRUD operations (6 tests)
- **`tests/conftest.py`**: Test fixtures and database setup

**Test Fixtures:**
- `test_engine`: Session-scoped SQLAlchemy engine
- `db_session`: Function-scoped session with automatic transaction rollback
- `real_db_session`: Alias for `db_session` (backward compatibility)

**Why Real Database Testing:**
- Validates actual PostgreSQL behavior (triggers, constraints, indexes)
- Catches schema compatibility issues
- Verifies query performance
- Tests transaction rollback behavior
- No mock maintenance burden

**Transaction Isolation:**
Each test runs in a transaction that is rolled back after completion, ensuring tests don't affect each other and run quickly.

### TypeScript Legacy

Some TypeScript files remain in the codebase (e.g., `PostgresDocumentRepository.ts`, `DataAccessFactory.ts`). These are legacy files from the migration and should eventually be removed. When working on repository or data access code, prefer the Python implementations in `src/axai_pg/`.

## Key Design Decisions

### 1. Migration from TypeScript to Python
The project was migrated from TypeScript/Node.js to Python/SQLAlchemy. When you encounter TypeScript files in the data layer, they are legacy artifacts.

### 2. Repository Pattern Over Direct ORM
Access to models goes through repository layer to enable:
- Caching with automatic invalidation
- Metrics collection
- Security enforcement
- Transaction management
- Query optimization

### 3. SQLAlchemy-First Schema with Real Database Testing
Models are the single source of truth for schema definition. The `PostgreSQLSchemaBuilder` creates the schema programmatically from SQLAlchemy models, including PostgreSQL-specific features (extensions, triggers, check constraints, indexes, comments).

All tests use real PostgreSQL (not mocks) to ensure:
- Schema compatibility with PostgreSQL-specific features
- Constraint validation (check constraints, foreign keys, unique constraints)
- Trigger functionality (auto-update timestamps)
- Query performance accuracy
- Transaction behavior correctness
- Extension functionality (uuid-ossp)

The old SQL files in `sql/schema/` are deprecated and kept only for reference. Schema creation is done exclusively through SQLAlchemy models.

### 4. UUID Primary Keys
All entities use UUIDs instead of auto-incrementing integers for:
- Better distributed system support
- No primary key conflicts across organizations
- Enhanced security (non-sequential IDs)

### 5. JSONB for Flexible Metadata
Documents have a `metadata` JSONB column for extensible attributes without schema changes.

## Development Workflow

### Making Changes to Models

1. Update the model class in `src/axai_pg/data/models/`
2. Create a Sqitch migration in `migrations/deploy/`
3. Create corresponding revert script in `migrations/revert/`
4. Create verify script in `migrations/verify/`
5. Test migration locally: `sqitch deploy` and `sqitch revert`
6. Update repository layer if needed
7. Write tests in `tests/integration/`
8. Update documentation

### Adding New Repository Methods

1. Add method to appropriate repository class
2. Apply `@track_metrics` decorator for monitoring
3. Configure caching if read-heavy operation
4. Add transaction support if multi-step operation
5. Write integration tests
6. Document in repository README

### Working with Database Sessions

Always use the session context manager pattern:

```python
from axai_pg import DatabaseManager

db = DatabaseManager.get_instance()

with db.session_scope() as session:
    # Perform operations
    # Automatic commit on success, rollback on exception
    pass
```

Never commit or rollback manually unless you have a specific reason.

## SQLAlchemy-First Schema Management

### Overview

The project uses **SQLAlchemy models as the single source of truth** for database schema. Schema is created programmatically, not from SQL files.

### PostgreSQLSchemaBuilder

Located in `src/axai_pg/utils/schema_builder.py`, this class creates the complete PostgreSQL schema from SQLAlchemy models:

```python
from src.axai_pg.utils.schema_builder import PostgreSQLSchemaBuilder
from sqlalchemy import create_engine

engine = create_engine("postgresql://user:pass@localhost/db")

# Create complete schema
PostgreSQLSchemaBuilder.build_complete_schema(engine)

# Drop complete schema
PostgreSQLSchemaBuilder.drop_complete_schema(engine)
```

### Schema Creation Steps

1. **Extensions**: Creates PostgreSQL extensions (uuid-ossp)
2. **Trigger Functions**: Creates custom trigger functions (update_modified_column)
3. **Tables**: Creates all tables from `Base.metadata.create_all()`
4. **Triggers**: Applies triggers to tables (auto-update timestamps)
5. **Comments**: Adds table and column comments
6. **Indexes**: Creates performance indexes

### Schema Features

All tables include:
- UUID primary keys (using uuid-ossp extension)
- Timestamps (created_at, updated_at with automatic trigger updates)
- Foreign key constraints with CASCADE deletes
- Check constraints (email format, status values, etc.)
- Performance indexes on foreign keys and query patterns
- JSONB columns for flexible metadata
- Table comments for documentation

### Migration from SQL Files

The SQL files in `sql/schema/` are **deprecated** and kept only for reference. All schema management is done through SQLAlchemy models and PostgreSQLSchemaBuilder.

**Do not modify SQL files.** Instead:
1. Update SQLAlchemy models in `src/axai_pg/data/models/`
2. Schema is automatically updated via PostgreSQLSchemaBuilder
3. Test changes with integration tests

### Testing Schema Changes

When modifying models:
1. Update the model class
2. Run integration tests to verify schema: `pytest tests/integration/test_schema_creation.py -v --integration`
3. PostgreSQLSchemaBuilder will create schema from updated models
4. Tests validate all PostgreSQL features work correctly

## Performance Considerations

### Connection Pooling
- Default pool size: 5
- Default max overflow: 5
- Pool timeout: 30 seconds
- Pool recycle: 1800 seconds (30 minutes)
- Pre-ping enabled for connection health checks

### Caching Strategy
- Read-heavy queries are cached
- Complex queries (related documents) have longer TTLs
- Write operations invalidate relevant cache entries
- Cache hit rates monitored for optimization

### Query Optimization
- Eager loading relationships when beneficial
- Pagination support for large result sets
- Indexes on foreign keys, frequently queried columns
- Monitoring for slow queries (>1s threshold)

## Docker Environment

### Container Names
- `axai-pg-test`: PostgreSQL test database (from docker-compose.yml)
- `axai-pg-standalone-test`: Standalone PostgreSQL for integration tests (from docker-compose.standalone-test.yml)

### Environment Variables
Configure via `.env` or `.env.test`:
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_SCHEMA` (defaults to "public")
- `POSTGRES_SSL_MODE` (defaults to "prefer")

## Important Notes

### Transaction Safety
- All repository methods use transactions
- Automatic rollback on any exception
- Monitor slow transactions (>1s logged)
- Avoid long-running transactions

### Security
- Never bypass repository layer for data access
- Always validate org_id context
- Use prepared statements (SQLAlchemy handles this)
- Audit logging for sensitive operations

### Schema Changes
- Use Sqitch migrations (not Alembic)
- Test migrations in both directions (deploy and revert)
- Consider performance impact on large tables
- Batch large data migrations
- Maintain backward compatibility

### Testing
- Write integration tests for all repository methods
- Test transaction rollback behavior
- Test multi-tenant isolation
- Test concurrent operations where relevant
- Use markers (`@pytest.mark.integration`, etc.)

## Common Issues

### "DatabaseManager not initialized"
Call `DatabaseManager.initialize(conn_config)` before using repositories or models.

### Test database not available
Ensure PostgreSQL container is running: `docker-compose -f docker-compose.standalone-test.yml up -d` or `./run_tests.sh`

### Migration conflicts
Use sequential versioning with date prefix to avoid conflicts. If conflict occurs, rebase migrations with new version numbers.

### Import errors
Ensure `PYTHONPATH` includes `src` directory. The package uses namespace structure with `src/axai_pg/`.

## Database Initialization for External Systems

The `DatabaseInitializer` utility (in `src/axai_pg/utils/db_initializer.py`) is designed for both testing and production database initialization. External systems can use this for integration testing.

### Quick Start for External Systems

```python
# Install with testing extras
# pip install axai-pg[testing]

from axai_pg.testing.fixtures import axai_db_session

def test_integration(axai_db_session):
    # Session with automatic rollback
    from axai_pg.data.models import Organization
    org = Organization(name="Test")
    axai_db_session.add(org)
    axai_db_session.commit()
    # Automatic rollback after test
```

### Programmatic Usage

```python
from axai_pg.utils import DatabaseInitializer, DatabaseInitializerConfig
from axai_pg.data.config.database import PostgresConnectionConfig

config = DatabaseInitializerConfig(
    connection_config=PostgresConnectionConfig.from_env(),
    auto_create_db=True,
    auto_drop_on_exit=True  # Cleanup after tests
)

with DatabaseInitializer(config) as db_init:
    db_init.setup_database()
    with db_init.session_scope() as session:
        # Run tests
        pass
```

### Available Pytest Fixtures

External systems can import these fixtures from `axai_pg.testing.fixtures`:
- `axai_db_config` - Connection configuration
- `axai_test_db` - Session-scoped database setup/teardown
- `axai_db_session` - Function-scoped session with rollback
- `axai_db_manager` - DatabaseManager instance
- `axai_clean_db_session` - Session without rollback
- `axai_reset_db` - Force database reset

### Docker Setup for Integration Tests

```bash
# Start standalone test database
docker-compose -f docker-compose.standalone-test.yml up -d

# Run tests
pytest tests/

# Cleanup
docker-compose -f docker-compose.standalone-test.yml down -v
```

### Environment Variables

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=test_db
POSTGRES_USER=test_user
POSTGRES_PASSWORD=test_password
AXAI_AUTO_DROP_DB=true          # Drop DB after tests
AXAI_LOAD_SAMPLE_DATA=false     # Load sample data
```

### DatabaseInitializer Methods

- `create_database()` - Create database if it doesn't exist
- `drop_database()` - Drop database
- `apply_schema(schema_file)` - Apply SQL schema
- `load_sample_data(script_path)` - Load test data
- `setup_database(load_sample_data, apply_schema)` - Complete setup
- `teardown_database()` - Cleanup and optionally drop
- `reset_database(load_sample_data)` - Drop and recreate
- `get_connection_config()` - Get connection configuration
- `get_database_manager()` - Get DatabaseManager instance
- `session_scope()` - Context manager for sessions

### Use Cases

1. **External System Integration Tests**: Use fixtures for clean, isolated tests
2. **CI/CD Pipelines**: Use docker-compose.standalone-test.yml
3. **Development Setup**: Initialize with sample data
4. **Production Deployment**: Initial database setup (see examples/production_init_example.py)
5. **Health Checks**: Verify database connectivity

### Examples

See `examples/` directory:
- `integration_test_example.py` - Multiple testing patterns
- `production_init_example.py` - Production scenarios

## Documentation References

- Database schema: `sql/schema/schema.sql`
- Schema documentation: `docs/schema/README.md`
- Migration guide: `migrations/MIGRATION_GUIDE.md`
- Repository pattern: `src/axai_pg/data/repositories/README.md`
- Integration spec: `docs/integration_spec.md`
- Performance testing: `sql/schema/perf_test_scenarios.md`
- Integration testing: `examples/integration_test_example.py`
- Production initialization: `examples/production_init_example.py`
