# PostgreSQL Data Access Layer Documentation

## Overview
This data access layer provides a robust interface for interacting with PostgreSQL in the document management system. It implements the repository pattern with both TypeORM (TypeScript) and SQLAlchemy (Python), offering type-safe database operations, connection pooling, and comprehensive error handling.

## Architecture

```mermaid
graph TD
    A[Application Code] --> B[Data Access Factory]
    B --> C[Document Repository]
    B --> D[Other Repositories...]
    C --> E[Connection Manager]
    D --> E
    E --> F[PostgreSQL Database]
    
    G[Python Code] --> H[SQLAlchemy DatabaseManager]
    H --> I[Session Factory]
    I --> J[Connection Pool]
    J --> F
```

## Implementation Options

### TypeScript Implementation (Legacy)
Uses TypeORM with repository pattern implementation.

### Python Implementation (New)
Uses SQLAlchemy with modern connection pooling and environment-based configuration.

## Key Components

### 1. TypeScript Components
#### Interfaces
- `IRepository<T>`: Base repository interface for CRUD operations
- `IDocumentRepository`: Document-specific repository with specialized operations

#### Implementation Classes
- `PostgresDocumentRepository`: Main implementation for document operations
- `PostgresConnectionManager`: Handles database connections and pooling
- `DataAccessFactory`: Creates and manages repository instances

#### Configuration
- `PostgresConfig`: Configuration management for database connections

### 2. Python SQLAlchemy Components
#### Core Classes
- `DatabaseManager`: Singleton manager for database connections and sessions
- `PostgresConnectionConfig`: Database connection configuration
- `PostgresPoolConfig`: Connection pool settings
- `AppSettings`: Environment-specific application settings

#### Configuration
Environment-based configuration with three profiles:
- Development: Optimized for development with debug features
- Test: Minimal pool for testing
- Production: Optimized for stability and performance

#### Health Monitoring
Built-in monitoring capabilities for:
- Connection pool statistics
- Query performance
- Error tracking
- Resource utilization

## Usage Examples

### Python SQLAlchemy Setup

#### Environment Configuration
```env
# Required environment variables
POSTGRES_HOST=your_host
POSTGRES_PORT=5432
POSTGRES_DB=your_database
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
APP_ENV=development|test|production

# Optional settings
DEBUG=false
LOG_SQL=false
DB_CONNECTION_TIMEOUT=30
```

#### Basic Database Operations
```python
from data.config.settings import Settings
from data.config.database import DatabaseManager

# Initialize with environment settings
settings = Settings.load()
DatabaseManager.initialize(settings.conn_config, settings.env_config.pool_config)

# Get database manager instance
db = DatabaseManager.get_instance()

# Use session for database operations
with db.session_scope() as session:
    # All operations in this block are transactional
    result = session.execute("SELECT * FROM documents").fetchall()
    
    # Automatic commit on success, rollback on exception
    session.execute(
        "INSERT INTO documents (title, content) VALUES (:title, :content)",
        {"title": "New Doc", "content": "Content..."}
    )
```

#### Health Checks and Monitoring
```python
# Get database health status
health_status = db.check_health()
print(f"Status: {health_status['status']}")
print(f"Pool stats: {health_status['pool']}")

# Connection metrics available in health_status:
# - pool.size: Current pool size
# - pool.checkedin: Available connections
# - pool.overflow: Current overflow connections
# - pool.checkedout: Active connections
```

### TypeScript Setup (Legacy)
```typescript
// Initialize connection manager
const connectionConfig = {
  host: 'localhost',
  port: 5432,
  database: 'docmanager',
  username: 'app_user',
  password: 'secure_password'
};

const connectionManager = PostgresConnectionManager.getInstance(connectionConfig);
const dataAccess = DataAccessFactory.getInstance(connectionManager);

// Get document repository
const documentRepo = await dataAccess.getDocumentRepository();
```

### Common Operations

#### Finding Documents
```typescript
// Find by ID
const document = await documentRepo.findById(123);

// Find by organization with options
const orgDocs = await documentRepo.findByOrganization(orgId, {
  limit: 20,
  offset: 0,
  includeSummaries: true,
  orderBy: { createdAt: 'DESC' }
});

// Find related documents
const relatedDocs = await documentRepo.findRelatedDocuments(documentId, 2);
```

#### Creating Documents
```typescript
// Create document with summary
const newDoc = await documentRepo.createWithSummary({
  title: 'New Document',
  content: 'Document content...',
  ownerId: userId,
  orgId: organizationId,
  documentType: 'article',
  status: 'draft'
}, {
  content: 'Document summary...',
  summaryType: 'abstract',
  toolAgent: 'summarizer-v1'
});
```

#### Updating Documents
```typescript
// Update with version tracking
const updatedDoc = await documentRepo.updateWithVersion(
  documentId,
  {
    title: 'Updated Title',
    content: 'Updated content...'
  },
  'Updated document title and content'
);
```

## Performance Considerations

### Connection Pooling
- Default pool size: 2-20 connections
- Suitable for dozens of concurrent users
- Configurable idle timeout: 30 seconds
- Connection acquisition timeout: 5 seconds

### Query Optimization
- Automatic query logging for operations exceeding 1 second
- Metrics tracking for monitoring performance
- Built-in connection pooling for efficient resource usage

### Caching
- Query result caching enabled (1-minute duration)
- Database-backed cache for consistency

## Security Features

### Query Safety
- Parameterized queries for SQL injection prevention
- Prepared statements for repeated operations
- Transaction support for data integrity

### Access Control
- Organization-level data isolation
- User ownership validation
- Role-based access control integration

## Error Handling

### Repository Layer
- Structured error handling with specific error types
- Transaction rollback on failures
- Detailed error logging
- Retry logic for transient failures

### Connection Management
- Automatic connection recovery
- Connection pool monitoring
- Health checks and diagnostics

## Monitoring and Metrics

### Available Metrics
- Operation counts
- Error rates
- Slow query detection
- Connection pool status

### Usage Example
```typescript
// Get metrics for document repository
const metrics = dataAccess.getMetrics('document');
console.log('Total operations:', metrics.operationCount);
console.log('Error count:', metrics.errorCount);
console.log('Slow queries:', metrics.slowQueryCount);
```

## Best Practices

1. **Connection Management**
   - Always use the connection manager instead of creating direct connections
   - Close connections properly when shutting down the application
   - Monitor connection pool metrics

2. **Transaction Handling**
   - Use transactions for operations that modify multiple records
   - Keep transactions short and focused
   - Handle rollbacks properly

3. **Error Handling**
   - Always catch and handle database errors appropriately
   - Log errors with sufficient context
   - Use type-safe error handling

4. **Query Optimization**
   - Monitor slow queries
   - Use appropriate indexes
   - Limit result sets with pagination

## Implementation Notes

- The data access layer is designed for a document management system with B2B multi-tenant requirements
- Performance is optimized for standard web response times (< 1 second)
- The implementation supports low concurrent user loads (dozens of users)
- The design focuses on maintainability and type safety
