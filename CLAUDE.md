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

# Using pipenv (if Pipfile exists)
pipenv install --dev
```

### Testing
```bash
# Start PostgreSQL test container
docker-compose --env-file .env.test up -d postgres

# Run all tests via script (includes unit, integration, and docker tests)
./run_tests.sh

# Run specific test types
pytest tests/unit/ -v                    # Unit tests only
pytest tests/integration/ -v             # Integration tests only
pytest tests/docker_integration/ -v      # Docker integration tests

# Run with markers
pytest -m unit                           # Tests marked as unit
pytest -m integration                    # Tests marked as integration
pytest -m db                             # Database-specific tests

# Run single test file
pytest tests/unit/test_models.py -v

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing

# Clean up test containers
docker-compose --env-file .env.test down
```

### Database Management
```bash
# Reset database (drops, recreates, applies schema)
./reset_db.sh

# Apply schema manually
docker exec axai-pg-test psql -U test_user -d test_db -f /docker-entrypoint-initdb.d/schema.sql

# Add sample data
python add_sample_data.py
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
# Start development environment with sample data
docker-compose --profile dev up -d

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

Three-tier testing approach:
1. **Unit tests** (`tests/unit/`): Isolated component testing
2. **Integration tests** (`tests/integration/`): Tests with real PostgreSQL database
3. **Docker integration tests** (`tests/docker_integration/`): Full containerized environment tests

Test configuration in `conftest.py` provides:
- Database session fixtures with automatic transaction rollback
- Sample data fixtures
- Test database setup/teardown

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

### 3. Real Database Testing
Integration tests use real PostgreSQL (not mocks) to ensure:
- Schema compatibility
- Constraint validation
- Query performance accuracy
- Transaction behavior correctness

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
- `axai-pg-test`: PostgreSQL test database
- `axai-pg-test-runner`: Test execution container
- `axai-pg-dev`: Development environment with sample data

### Network Configuration
Uses external `shared-network` for inter-container communication.

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
Ensure PostgreSQL container is running: `docker-compose --env-file .env.test up -d postgres`

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
