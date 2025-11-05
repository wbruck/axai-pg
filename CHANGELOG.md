# Changelog

All notable changes to the AXAI PostgreSQL Models project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Removed
- Legacy TypeScript implementation files (DataAccessFactory.ts, PostgresConnectionManager.ts, etc.)
- TypeScript test files from `src/axai_pg/data/__tests__/`
- TypeScript interfaces directory
- Duplicate User model in `src/axai_pg/models/`
- Empty placeholder directories (`src/axai_pg/core/`, `src/axai_pg/api/`, `src/axai_pg/services/`)
- Empty log files from logs directory
- Stale Python cache directories

### Changed
- Moved TypeScript to Python migration scripts to `archive/migration/`
- Moved completed planning documents (TODO.md, CURRENT_PLAN.md) to `archive/`
- Reorganized documentation:
  - `db_usage_guide.md` → `docs/operations/`
  - `backup_recovery.md` → `docs/operations/`
  - `schema_readme.md` → `docs/schema/`
- Relocated `test_repository_factory.py` from `src/tests/` to `tests/integration/`
- Updated imports in test_repository_factory.py to use absolute imports

### Added
- This CHANGELOG.md file
- Archive directory for historical migration artifacts
- docs/operations/ directory for operational documentation

## [0.1.0] - 2025-01-04

### Added
- Complete SQLAlchemy 2.0 model implementation
- PostgreSQLSchemaBuilder for programmatic schema creation
- Repository pattern with BaseRepository and DocumentRepository
- DatabaseManager singleton for connection management
- DatabaseInitializer for testing and production setup
- Comprehensive integration test suite (40 tests)
- Multi-tenant architecture with organization-level isolation
- Connection pooling with configurable parameters
- Metrics collection and monitoring decorators
- Pytest fixtures for external system integration testing
- Docker Compose configurations for testing and development
- Extensive documentation (CLAUDE.md, README.md, integration specs)

### Changed
- Migrated from TypeScript/TypeORM to Python/SQLAlchemy
- Changed from SQL-first to SQLAlchemy-first schema approach
- Switched from unit tests with mocks to integration tests with real PostgreSQL

### Deprecated
- SQL schema files in `sql/schema/` (kept for reference only)

## Notes

### Migration Status
The project completed a full migration from TypeScript to Python in early 2025. All TypeScript code has been replaced with Python implementations. The migration artifacts have been archived for reference.

### Schema Management
The project uses SQLAlchemy models as the single source of truth. Schema is created programmatically via `PostgreSQLSchemaBuilder.build_complete_schema()`.

### Testing Philosophy
All tests use real PostgreSQL databases with no mocking. This ensures tests validate actual database behavior, constraints, triggers, and PostgreSQL-specific features.
