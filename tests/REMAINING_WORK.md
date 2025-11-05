# Remaining Test Work - SQLAlchemy-First Migration

## Completed ✅

1. **Fixed critical import bug** - `document.py` now imports JSON for DocumentVersion
2. **Updated conftest.py** - Now uses `PostgreSQLSchemaBuilder` instead of `Base.metadata.create_all()`
3. **Added `real_db_session` fixture** - Backward compatibility alias for `db_session`
4. **Created comprehensive schema tests** - `tests/integration/test_schema_creation.py` (16 tests, all passing ✅):
   - All tables exist
   - UUID extension installed
   - Triggers work (auto-update timestamps)
   - Check constraints enforced (email, status, version, etc.)
   - Indexes created
   - Foreign keys work
   - Cascade deletes work
   - Unique constraints enforced
   - JSONB columns work
   - Table comments exist
5. **Fixed database authentication** - `conftest.py` now uses correct test_user:test_password credentials
6. **Removed exception swallowing** - `PostgreSQLSchemaBuilder` now propagates exceptions for better debugging
7. **Made coverage optional** - `pytest.ini` no longer requires pytest-cov
8. **Fixed UUID type mismatches** - All models in `security.py` now use UUID instead of Integer
9. **Updated README.md** - Added installation instructions and SQLAlchemy-first testing documentation

## TODO - Additional Test Files

### 1. tests/integration/test_schema_builder.py
Test the PostgreSQLSchemaBuilder class directly:

```python
@pytest.mark.integration
class TestPostgreSQLSchemaBuilder:
    def test_build_complete_schema_success(self, test_engine):
        # Drop existing, build fresh
        PostgreSQLSchemaBuilder.drop_complete_schema(test_engine)
        success = PostgreSQLSchemaBuilder.build_complete_schema(test_engine)
        assert success is True

    def test_build_schema_is_idempotent(self, test_engine):
        # Can run multiple times safely
        success1 = PostgreSQLSchemaBuilder.build_complete_schema(test_engine)
        success2 = PostgreSQLSchemaBuilder.build_complete_schema(test_engine)
        assert success1 and success2

    def test_create_extensions(self, test_engine):
        # Test individual method
        PostgreSQLSchemaBuilder.create_extensions(test_engine)
        # Verify uuid-ossp exists

    def test_create_triggers(self, test_engine):
        # Test trigger creation
        PostgreSQLSchemaBuilder.create_table_triggers(test_engine)
        # Verify triggers exist

    # Similar tests for indexes, comments, etc.
```

### 2. tests/integration/test_database_initializer_sqlalchemy.py
Test DatabaseInitializer with both approaches:

```python
@pytest.mark.integration
class TestDatabaseInitializerSQLAlchemy:
    def test_initializer_with_sqlalchemy(self):
        # Test use_sqlalchemy=True (default)
        config = DatabaseInitializerConfig(
            connection_config=PostgresConnectionConfig.from_env(),
            auto_create_db=True,
            auto_drop_on_exit=True
        )
        with DatabaseInitializer(config) as db_init:
            db_init.setup_database()  # Should use SQLAlchemy
            # Verify schema exists

    def test_initializer_with_sql_file(self):
        # Test use_sqlalchemy=False (backward compat)
        config = DatabaseInitializerConfig(...)
        with DatabaseInitializer(config) as db_init:
            db_init.apply_schema(use_sqlalchemy=False)
            # Verify schema exists

    def test_both_approaches_create_same_schema(self):
        # Create with SQLAlchemy, verify tables
        # Drop
        # Create with SQL file, verify same tables
        # Both should be identical
```

## TODO - Convert/Move Unit Tests

### Current tests/unit/ files to convert:

1. **test_base_repository.py**
   - Remove all mocks
   - Use real db_session fixture
   - Move to tests/integration/
   - Test actual repository operations with real DB

2. **test_document_repository.py**
   - Remove all mocks
   - Use real db_session fixture
   - Move to tests/integration/
   - Test document queries with real data

3. **test_database_connection.py**
   - Most tests already covered by DatabaseManager
   - Keep only unique connection pool tests
   - Move to tests/integration/

4. **test_database_monitoring.py**
   - Review content
   - Keep if testing unique monitoring features
   - Otherwise consolidate into other tests

### Steps for each file:
```bash
# 1. Remove mock imports and fixtures
# 2. Replace with real db_session fixture
# 3. Create real test data in each test
# 4. Move file to tests/integration/
# 5. Add @pytest.mark.integration decorator
```

## TODO - Remove Duplicates

### Duplicate tests to consolidate:

1. **User creation tests** - Exists in:
   - tests/test_models.py
   - tests/test_crud_operations.py
   - tests/integration/test_database.py
   - tests/docker_integration/test_docker_database.py

   **Action**: Keep one comprehensive test in test_crud_operations.py, remove others

2. **Connection tests** - Multiple basic connection tests

   **Action**: One test in test_database_connection.py is enough

3. **Document CRUD** - Similar tests across files

   **Action**: Consolidate into test_crud_operations.py

## TODO - Clean Up

1. **Delete tests/unit/ directory** after moving all tests to integration
2. **Update pytest.ini** if needed to reflect new structure
3. **Update run_tests.sh** to remove unit/integration distinction (all are integration now)
4. **Update README.md** testing section to reflect "all tests use real PostgreSQL"

## TODO - Update Documentation

1. **README.md** - Update testing section:
   ```markdown
   ## Testing

   All tests use a real PostgreSQL database for accuracy.

   ### Running Tests
   ```bash
   # Start database
   docker-compose -f docker-compose.standalone-test.yml up -d

   # Run all tests
   pytest tests/ -v --integration

   # Run specific tests
   pytest tests/integration/test_schema_creation.py -v
   ```

2. **CLAUDE.md** - Add section on SQLAlchemy-first testing:
   ```markdown
   ## Testing with SQLAlchemy-First Approach

   All tests use real PostgreSQL, no mocks.
   Schema created via PostgreSQLSchemaBuilder.
   Tests verify actual database behavior.
   ```

## Commands to Run

After completing remaining work:

```bash
# Test schema creation
pytest tests/integration/test_schema_creation.py -v --integration

# Test schema builder (once created)
pytest tests/integration/test_schema_builder.py -v --integration

# Test database initializer (once created)
pytest tests/integration/test_database_initializer_sqlalchemy.py -v --integration

# Run all tests
pytest tests/ -v --integration

# Verify no mocks remain
grep -r "mock" tests/ --include="*.py" | grep -v "# mock" | grep -v "REMAINING_WORK"
```

## Success Criteria

- ✅ All tests pass with real PostgreSQL
- ✅ No mock fixtures remain
- ✅ Schema created via SQLAlchemy verified
- ✅ Triggers, constraints, indexes all tested
- ✅ Both SQLAlchemy and SQL file approaches tested
- ✅ No duplicate tests
- ✅ Clean test structure (only integration tests)
- ✅ Documentation updated

## Priority Order

1. **HIGH**: Create test_schema_builder.py (tests core functionality)
2. **HIGH**: Create test_database_initializer_sqlalchemy.py (tests both approaches)
3. **MEDIUM**: Convert unit tests to integration tests
4. **MEDIUM**: Remove duplicate tests
5. **LOW**: Clean up directory structure
6. **LOW**: Update documentation
