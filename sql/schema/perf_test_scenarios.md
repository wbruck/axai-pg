# Performance Test Scenarios

## Test Setup Requirements

1. Sample Data Volume
   - Organizations: 3-5
   - Users per org: 5-10
   - Documents per org: 1000-2000
   - Summaries per document: 2-3
   - Topics: 15-20
   - Document-topic associations: 3-5 per document

## Key Test Scenarios

1. Document Retrieval Tests
   ```sql
   -- Test Case 1: Organization Document List
   -- Expected time: < 100ms
   SELECT d.title, d.status, u.username 
   FROM documents d 
   JOIN users u ON d.owner_id = u.id 
   WHERE d.org_id = 1
   ORDER BY d.created_at DESC
   LIMIT 20;

   -- Test Case 2: Full-Text Search
   -- Expected time: < 800ms
   SELECT d.title, d.content
   FROM documents d
   WHERE to_tsvector('english', d.content) @@ to_tsquery('english', 'technology & analysis')
   LIMIT 10;
   ```

2. Topic Analysis Tests
   ```sql
   -- Test Case 3: Topic-Based Document Search
   -- Expected time: < 300ms
   SELECT d.title, t.name, dt.relevance_score
   FROM documents d
   JOIN document_topics dt ON d.id = dt.document_id
   JOIN topics t ON dt.topic_id = t.id
   WHERE t.name = 'Artificial Intelligence'
   ORDER BY dt.relevance_score DESC
   LIMIT 10;
   ```

3. Summary Retrieval Tests
   ```sql
   -- Test Case 4: Document Summaries
   -- Expected time: < 200ms
   SELECT d.title, s.summary_type, s.content
   FROM documents d
   JOIN summaries s ON d.id = s.document_id
   WHERE d.status = 'published'
   AND s.tool_agent = 'gpt-4'
   LIMIT 10;
   ```

## Load Testing Guidelines

1. Concurrent User Simulation
   - Steady state: 20 concurrent users
   - Peak load: 50 concurrent users
   - Operation mix: 70% reads, 30% writes

2. Key Metrics to Monitor
   - Query execution time
   - PostgreSQL connection count
   - Buffer cache hit ratio
   - Index usage statistics

3. Success Criteria
   - 95th percentile response time < 1 second
   - No query timeouts under normal load
   - Buffer cache hit ratio > 95%
   - No significant query plan changes under load

## Test Data Requirements

1. Document Content Variety
   - Short documents (< 1000 words)
   - Medium documents (1000-5000 words)
   - Long documents (> 5000 words)
   - Various document types and formats

2. Topic Distribution
   - Mix of broad and specific topics
   - Varied relevance scores
   - Multiple topics per document

3. Summary Coverage
   - Multiple summary types per document
   - Various tool agents
   - Different confidence scores

## Test Implementation Notes

1. Performance Monitoring
   ```sql
   -- Monitor query times
   SELECT query, calls, total_time/calls as avg_time_ms, rows/calls as avg_rows
   FROM pg_stat_statements
   ORDER BY total_time/calls DESC
   LIMIT 10;

   -- Check index usage
   SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
   FROM pg_stat_user_indexes
   ORDER BY idx_scan DESC;
   ```

2. Test Data Generation
   - Use realistic text content
   - Maintain referential integrity
   - Include edge cases in data distribution

Remember: Run tests multiple times and average results to account for variations in database performance.
