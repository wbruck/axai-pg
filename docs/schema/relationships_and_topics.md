# Document Relationships and Topic Management

## Graph Structure

The system uses a flexible graph structure to represent relationships between documents, implemented using relational tables.

### Graph Nodes
```sql
CREATE TABLE graph_nodes (
  id SERIAL PRIMARY KEY,
  document_id INTEGER REFERENCES documents(id) ON DELETE SET NULL,
  node_type VARCHAR(50) NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  properties JSONB,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  created_by_tool VARCHAR(100) NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE
);
```
- **Primary Key**: `id` (auto-incrementing)
- **Foreign Keys**: `document_id` references documents (allows NULL)
- **Usage**: Represents vertices in the document relationship graph
- **Node Types**: Can represent documents, concepts, or other entities
- **Properties**: Flexible JSONB field for additional attributes

### Graph Relationships
```sql
CREATE TABLE graph_relationships (
  id SERIAL PRIMARY KEY,
  source_node_id INTEGER NOT NULL REFERENCES graph_nodes(id) ON DELETE CASCADE,
  target_node_id INTEGER NOT NULL REFERENCES graph_nodes(id) ON DELETE CASCADE,
  relationship_type VARCHAR(50) NOT NULL,
  is_directed BOOLEAN NOT NULL DEFAULT TRUE,
  weight DECIMAL(10,5),
  confidence_score DECIMAL(5,4),
  properties JSONB,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  created_by_tool VARCHAR(100) NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE
);
```
- **Primary Key**: `id` (auto-incrementing)
- **Foreign Keys**: 
  - `source_node_id` references graph_nodes
  - `target_node_id` references graph_nodes
- **Usage**: Represents edges in the document relationship graph
- **Features**:
  - Supports both directed and undirected relationships
  - Includes weight and confidence scoring
  - Tracks creating tool/agent

## Topics and Clustering

### Topics
```sql
CREATE TABLE topics (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  description TEXT,
  keywords TEXT[],
  parent_topic_id INTEGER REFERENCES topics(id),
  extraction_method VARCHAR(50),
  global_importance DECIMAL(5,4),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  created_by_tool VARCHAR(100),
  is_active BOOLEAN NOT NULL DEFAULT TRUE
);
```
- **Primary Key**: `id` (auto-incrementing)
- **Foreign Keys**: `parent_topic_id` references topics (hierarchical structure)
- **Usage**: Represents topics identified across documents
- **Features**:
  - Hierarchical topic structure
  - Keyword arrays for topic identification
  - Global importance scoring

### Document-Topic Relationships
```sql
CREATE TABLE document_topics (
  id SERIAL PRIMARY KEY,
  document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
  relevance_score DECIMAL(5,4) NOT NULL,
  context JSONB,
  extracted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  extracted_by_tool VARCHAR(100) NOT NULL,
  UNIQUE(document_id, topic_id)
);
```
- **Primary Key**: `id` (auto-incrementing)
- **Foreign Keys**:
  - `document_id` references documents
  - `topic_id` references topics
- **Usage**: Maps documents to topics with relevance scores
- **Features**:
  - Prevents duplicate topic assignments
  - Includes contextual information
  - Tracks extracting tool/agent

### Document Clusters
```sql
CREATE TABLE document_clusters (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  algorithm VARCHAR(50) NOT NULL,
  parameters JSONB,
  validity_metrics JSONB,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  created_by_tool VARCHAR(100) NOT NULL,
  version INTEGER NOT NULL DEFAULT 1
);
```
- **Primary Key**: `id` (auto-incrementing)
- **Usage**: Represents groups of related documents
- **Features**:
  - Tracks clustering algorithm and parameters
  - Stores cluster validity metrics
  - Supports versioning of clusters

### Cluster Membership
```sql
CREATE TABLE document_cluster_members (
  id SERIAL PRIMARY KEY,
  document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  cluster_id INTEGER NOT NULL REFERENCES document_clusters(id) ON DELETE CASCADE,
  membership_score DECIMAL(5,4) NOT NULL,
  distance_from_centroid DECIMAL(10,6),
  assignment_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  is_primary_cluster BOOLEAN DEFAULT FALSE,
  UNIQUE(document_id, cluster_id)
);
```
- **Primary Key**: `id` (auto-incrementing)
- **Foreign Keys**:
  - `document_id` references documents
  - `cluster_id` references document_clusters
- **Usage**: Maps documents to clusters with membership scores
- **Features**:
  - Prevents duplicate cluster assignments
  - Tracks distance from cluster centroid
  - Identifies primary cluster assignment

## Common Query Patterns

### Graph Traversal

1. Find directly related documents:
```sql
WITH document_nodes AS (
  SELECT id FROM graph_nodes WHERE document_id = $1
)
SELECT DISTINCT d.*
FROM documents d
JOIN graph_nodes gn ON d.id = gn.document_id
WHERE gn.id IN (
  SELECT target_node_id
  FROM graph_relationships
  WHERE source_node_id IN (SELECT id FROM document_nodes)
  UNION
  SELECT source_node_id
  FROM graph_relationships
  WHERE target_node_id IN (SELECT id FROM document_nodes)
);
```

2. Find documents by topic similarity:
```sql
SELECT d.*, dt.relevance_score
FROM documents d
JOIN document_topics dt ON d.id = dt.document_id
WHERE dt.topic_id IN (
  SELECT topic_id
  FROM document_topics
  WHERE document_id = $1
  AND relevance_score >= 0.7
)
AND d.id != $1
ORDER BY dt.relevance_score DESC;
```

3. Find documents in same cluster:
```sql
SELECT d.*, dcm.membership_score
FROM documents d
JOIN document_cluster_members dcm ON d.id = dcm.document_id
WHERE dcm.cluster_id IN (
  SELECT cluster_id
  FROM document_cluster_members
  WHERE document_id = $1
  AND is_primary_cluster = true
)
AND d.id != $1
ORDER BY dcm.membership_score DESC;
```

## Performance Optimization

### Key Indexes
```sql
-- Graph traversal optimization
CREATE INDEX idx_graph_nodes_document ON graph_nodes(document_id) WHERE document_id IS NOT NULL;
CREATE INDEX idx_graph_relationships_source ON graph_relationships(source_node_id);
CREATE INDEX idx_graph_relationships_target ON graph_relationships(target_node_id);
CREATE INDEX idx_graph_relationships_type ON graph_relationships(relationship_type);

-- Topic and cluster lookup optimization
CREATE INDEX idx_document_topics_document ON document_topics(document_id);
CREATE INDEX idx_document_topics_topic ON document_topics(topic_id);
CREATE INDEX idx_document_topics_relevance ON document_topics(relevance_score DESC);
CREATE INDEX idx_document_cluster_members_document ON document_cluster_members(document_id);
CREATE INDEX idx_document_cluster_members_cluster ON document_cluster_members(cluster_id);
```

### Query Optimization Tips

1. Use CTEs for complex graph traversals
2. Consider path length limits in recursive queries
3. Use appropriate indexes for relationship traversal
4. Implement materialized paths for frequent deep traversals
5. Cache frequently accessed topic/cluster relationships

## Best Practices

### Graph Management

1. Keep node types consistent and documented
2. Use meaningful relationship types
3. Consider relationship direction carefully
4. Maintain reasonable confidence thresholds
5. Regular cleanup of inactive relationships

### Topic and Cluster Management

1. Regular review and cleanup of unused topics
2. Maintain topic hierarchy depth limits
3. Document clustering algorithm parameters
4. Regular validation of cluster quality
5. Archive or remove outdated clusters
