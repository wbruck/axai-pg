# Complete SQLAlchemy-First Migration - Remaining Work

## Overview
Complete the test suite migration to SQLAlchemy-first approach by creating new test files, converting unit tests to integration tests, removing duplicates, and cleaning up the test structure.

## Phase 1: Create New High-Priority Test Files (HIGH) ✅ COMPLETED

### 1.1 Create `tests/integration/test_schema_builder.py`
Test PostgreSQLSchemaBuilder class directly with 8-10 tests:

**Tests to implement:**
- `test_build_complete_schema_success` - Verify full schema creation works
- `test_build_schema_is_idempotent` - Can run multiple times safely
- `test_drop_complete_schema` - Verify cleanup works
- `test_create_extensions` - Test uuid-ossp extension creation
- `test_create_update_timestamp_trigger` - Test trigger function creation
- `test_create_table_triggers` - Test trigger application to tables
- `test_add_table_comments` - Test comment addition
- `test_create_performance_indexes` - Test index creation
- `test_schema_builder_with_empty_database` - Start from scratch
- `test_schema_builder_with_existing_schema` - Handle existing schema

**Implementation approach:**
- Use `test_engine` fixture from conftest
- Create separate database connection for isolation
- Test individual methods in isolation where possible
- Verify results by querying pg_catalog tables

### 1.2 Create `tests/integration/test_database_initializer.py`
Test DatabaseInitializer with 6-8 tests:

**Tests to implement:**
- `test_initializer_with_sqlalchemy_default` - Test use_sqlalchemy=True (default)
- `test_initializer_with_sql_file` - Test use_sqlalchemy=False (backward compat)
- `test_context_manager_auto_cleanup` - Test auto_drop_on_exit=True
- `test_context_manager_no_cleanup` - Test auto_drop_on_exit=False
- `test_setup_database_creates_all_tables` - Verify all tables created
- `test_health_check_passes` - Test health check functionality
- `test_both_approaches_create_same_schema` - Compare SQLAlchemy vs SQL file
- `test_database_manager_integration` - Test get_database_manager() works

**Implementation approach:**
- Use unique database names for each test (test_init_1, test_init_2, etc.)
- Create temporary databases for testing
- Clean up after each test manually
- Compare table lists and schemas between approaches

---

## Phase 2: Convert Unit Tests to Integration Tests (MEDIUM) 📋 TODO

### 2.1 Convert `tests/unit/test_base_repository.py`
**Current state:** Uses mocks extensively (mock_db_session, mock_metrics)

**Conversion steps:**
1. Remove all mock imports (`unittest.mock`)
2. Remove all mock fixtures (mock_db_session, mock_metrics, mock_user, simulate_db_error)
3. Replace with `db_session` fixture from conftest
4. Create real test data in each test (Organization, User instances)
5. Test actual repository operations with real DB
6. Add `@pytest.mark.integration` decorator
7. Remove `@pytest.mark.asyncio` if not needed (check if methods are actually async)
8. Move file to `tests/integration/test_base_repository.py`

**Expected tests (~10-12):**
- find_by_id with existing record
- find_by_id with non-existent record
- create new entity
- update existing entity
- delete entity
- find_all with pagination
- count entities
- Repository caching behavior

### 2.2 Convert `tests/unit/test_document_repository.py`
**Current state:** Uses mocks

**Conversion steps:**
1. Same as 2.1 - remove mocks
2. Create real Organization, User, Document instances
3. Test document-specific queries with real data
4. Test relationships (owner, organization, versions, summaries)
5. Move to `tests/integration/test_document_repository.py`

**Expected tests (~8-10):**
- Document CRUD operations
- Query documents by org_id
- Query documents by owner_id
- Query documents by status
- Document relationships work correctly

### 2.3 Convert `tests/unit/test_database_connection.py`
**Current state:** Tests connection pooling

**Conversion approach:**
1. Review content first - determine what's unique vs redundant
2. Keep only unique connection pool tests
3. Remove tests already covered by DatabaseManager
4. Convert remaining tests to use real database
5. Move to `tests/integration/test_database_connection.py`

**Expected tests (~4-6):**
- Connection pool configuration
- Connection pool max connections
- Connection timeout behavior
- Connection retry logic

### 2.4 Review `tests/unit/test_database_monitoring.py`
**Conversion approach:**
1. Review content to determine if still needed
2. If unique monitoring features: convert to integration test
3. If redundant: delete file, consolidate features into other tests
4. If kept: move to `tests/integration/test_database_monitoring.py`

---

## Phase 3: Remove Duplicate Tests (MEDIUM) 📋 TODO

### 3.1 Consolidate User Creation Tests
**Files containing duplicate tests:**
- `tests/test_models.py`
- `tests/test_crud_operations.py`
- `tests/integration/test_database.py`
- `tests/docker_integration/test_docker_database.py`

**Action:**
1. Review each file to identify which tests are duplicates
2. Keep the most comprehensive version in `tests/integration/test_crud_operations.py`
3. Delete duplicate tests from other files
4. If files become empty, mark for deletion in Phase 4

### 3.2 Consolidate Connection Tests
**Action:**
1. Identify all connection tests across test files
2. Keep one comprehensive connection test in `tests/integration/test_database_connection.py`
3. Remove duplicates

### 3.3 Consolidate Document CRUD Tests
**Action:**
1. Find all document CRUD tests
2. Consolidate into `tests/integration/test_crud_operations.py` or `tests/integration/test_document_repository.py`
3. Remove duplicates

---

## Phase 4: Clean Up Directory Structure (LOW) 📋 TODO

### 4.1 Delete Unit Tests Directory
**After** all tests are converted:
```bash
rm -rf tests/unit/
```

### 4.2 Review and Clean Root Test Files
Files to review:
- `tests/test_models.py` - Move useful tests to integration/, delete if empty
- `tests/test_crud_operations.py` - Move to integration/, or keep if already integration-style
- `tests/integration/test_database.py` - Review for duplicates, consolidate

### 4.3 Review Docker Tests
- `tests/docker_integration/test_docker_database.py` - Determine if still needed or redundant

### 4.4 Update `run_tests.sh`
Current state likely has unit/integration distinction

**Changes needed:**
- Remove separate unit/integration test commands
- Update to run all tests with `--integration` flag
- Simplify to single test command since all are integration now
- Update help text

---

## Phase 5: Update Documentation (LOW) 📋 TODO

### 5.1 Update CLAUDE.md
Add section on SQLAlchemy-first testing:
- All tests use real PostgreSQL
- No mocks in test suite
- Schema created via PostgreSQLSchemaBuilder
- Tests verify actual database behavior
- Test organization structure

### 5.2 Final README.md updates
Already mostly done, but verify:
- Testing section is complete
- No references to deprecated SQL files
- All commands are correct
- Test organization is documented

### 5.3 Update REMAINING_WORK.md
Mark all items as completed and archive the file or rename to COMPLETED_WORK.md

---

## Execution Order

**Session 1: High-Priority Tests (1-2 hours)** ✅ COMPLETED
1. ✅ Created test_schema_builder.py (10 tests, all passing)
2. ✅ Created test_database_initializer.py (7 passing, 1 skipped)
3. ✅ All Phase 1 tests verified passing

**Session 2: Convert Unit Tests (2-3 hours)** 📋 TODO
1. Convert test_base_repository.py
2. Convert test_document_repository.py
3. Convert test_database_connection.py
4. Review test_database_monitoring.py

**Session 3: Remove Duplicates (1 hour)** 📋 TODO
1. Consolidate user creation tests
2. Consolidate connection tests
3. Consolidate document CRUD tests
4. Run all tests to ensure nothing broken

**Session 4: Clean Up (30 min - 1 hour)** 📋 TODO
1. Delete tests/unit/ directory
2. Clean up root test files
3. Update run_tests.sh
4. Run final test suite

**Session 5: Documentation (30 min)** 📋 TODO
1. Update CLAUDE.md
2. Final README.md check
3. Archive REMAINING_WORK.md

---

## Success Criteria

- [ ] All tests pass with real PostgreSQL
- [ ] No mock fixtures remain in entire test suite
- [ ] Schema created via SQLAlchemy verified
- [ ] Both SQLAlchemy and SQL file approaches tested
- [ ] No duplicate tests
- [ ] Clean test structure (tests/integration/ only)
- [ ] tests/unit/ directory deleted
- [ ] Documentation updated
- [ ] run_tests.sh simplified

---

## Estimated Total Time
- Phase 1: 1-2 hours ⏳ IN PROGRESS
- Phase 2: 2-3 hours 📋 TODO
- Phase 3: 1 hour 📋 TODO
- Phase 4: 30 min - 1 hour 📋 TODO
- Phase 5: 30 min 📋 TODO

**Total: 5-7 hours**

---

## Progress Tracking

### Completed ✅
- Fixed database authentication in conftest.py
- Removed exception swallowing in schema_builder.py
- Made coverage optional in pytest.ini
- Fixed UUID type mismatches in security.py models
- Fixed timestamp trigger test
- Added installation instructions to README.md
- Updated tests/REMAINING_WORK.md with progress
- All 16 schema creation tests passing

### In Progress ⏳
- None - awaiting Phase 2 approval

### Todo 📋
- Phases 2-5 (see above)
