# Data Integrity and Versioning

## Document Version Control

The system maintains a complete version history for documents using the `document_versions` table:

```sql
CREATE TABLE document_versions (
  id SERIAL PRIMARY KEY,
  document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  version INTEGER NOT NULL,
  content TEXT NOT NULL,
  title TEXT NOT NULL,
  status VARCHAR(20) NOT NULL,
  modified_by INTEGER NOT NULL REFERENCES users(id),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  change_description TEXT
);
```

### Version Control Features
- Complete historical record of document changes
- Tracks both content and metadata changes
- Links modifications to specific users
- Maintains change descriptions
- Cascading deletion with parent document

### Versioning Best Practices
1. Always increment document version when content changes
2. Include meaningful change descriptions
3. Maintain version history for audit purposes
4. Use transactions when updating versions

## Data Integrity Constraints

### Organization Constraints
```sql
CONSTRAINT organizations_name_not_empty CHECK (length(trim(name)) > 0)
```
- Ensures organization names are non-empty
- Prevents whitespace-only names

### User Constraints
```sql
CONSTRAINT users_username_not_empty CHECK (length(trim(username)) > 0)
CONSTRAINT users_email_valid CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
```
- Ensures valid usernames
- Validates email format
- Enforces unique usernames and emails

### Document Constraints
```sql
CONSTRAINT documents_title_not_empty CHECK (length(trim(title)) > 0)
CONSTRAINT documents_valid_status CHECK (status IN ('draft', 'published', 'archived', 'deleted'))
CONSTRAINT documents_valid_version CHECK (version > 0)
CONSTRAINT documents_valid_processing_status CHECK (processing_status IN ('pending', 'processing', 'complete', 'error'))
```
- Ensures document titles are non-empty
- Enforces valid document statuses
- Requires positive version numbers
- Validates processing status values

## Referential Integrity

### Organization Hierarchy
- Users must belong to valid organizations
- Documents must belong to valid organizations and users
```sql
org_id INTEGER NOT NULL REFERENCES organizations(id)
owner_id INTEGER NOT NULL REFERENCES users(id)
```

### Document References
- Summaries reference valid documents
- Graph nodes optionally reference documents
- Topic and cluster memberships reference valid documents
```sql
document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE
```

## Automatic Timestamp Management

The schema includes automatic timestamp management for tracking creation and updates:

1. Creation Timestamps
```sql
created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
```

2. Update Timestamps
```sql
updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
```

3. Automatic Update Trigger
```sql
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

## Common Version Control Operations

### Creating a New Version
```sql
BEGIN;
-- Update document version
UPDATE documents 
SET version = version + 1,
    content = $1,
    title = $2,
    status = $3
WHERE id = $4;

-- Insert version history
INSERT INTO document_versions 
(document_id, version, content, title, status, modified_by, change_description)
VALUES 
($4, (SELECT version FROM documents WHERE id = $4), $1, $2, $3, $5, $6);
COMMIT;
```

### Retrieving Version History
```sql
-- Get complete version history
SELECT dv.*, u.username as modified_by_user
FROM document_versions dv
JOIN users u ON dv.modified_by = u.id
WHERE dv.document_id = $1
ORDER BY dv.version DESC;

-- Get specific version
SELECT dv.*, u.username as modified_by_user
FROM document_versions dv
JOIN users u ON dv.modified_by = u.id
WHERE dv.document_id = $1
AND dv.version = $2;
```

### Comparing Versions
```sql
SELECT 
  dv1.version as old_version,
  dv2.version as new_version,
  dv1.title as old_title,
  dv2.title as new_title,
  dv1.content as old_content,
  dv2.content as new_content,
  dv1.status as old_status,
  dv2.status as new_status,
  u.username as modified_by
FROM document_versions dv1
JOIN document_versions dv2 ON dv1.document_id = dv2.document_id
JOIN users u ON dv2.modified_by = u.id
WHERE dv1.document_id = $1
AND dv1.version = $2
AND dv2.version = $3;
```

## Best Practices

### Version Control
1. Always create versions through transactions
2. Include meaningful change descriptions
3. Maintain complete version history
4. Use appropriate version numbering

### Data Integrity
1. Use constraints to enforce business rules
2. Implement appropriate foreign key relationships
3. Include cascading deletes where appropriate
4. Validate data before insertion

### Timestamp Management
1. Use built-in timestamp functions
2. Include timezone information
3. Implement update triggers consistently
4. Use timestamps for audit trails

### Security
1. Implement row-level security where needed
2. Use appropriate NULL constraints
3. Validate input data
4. Maintain audit trails
