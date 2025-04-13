import { PostgresDocumentRepository } from '../repositories/PostgresDocumentRepository';
import { PostgresConnectionManager } from '../PostgresConnectionManager';
import { Document } from '../interfaces/IDocumentRepository';
import { Connection } from 'typeorm';

describe('PostgresDocumentRepository', () => {
  let repository: PostgresDocumentRepository;
  let connectionManager: PostgresConnectionManager;
  let connection: Connection;

  // Test data
  const testDoc: Omit<Document, 'id'> = {
    title: 'Test Document',
    content: 'Test content',
    ownerId: 1,
    orgId: 1,
    documentType: 'article',
    status: 'draft',
    version: 1,
    createdAt: new Date(),
    updatedAt: new Date(),
    processingStatus: 'pending'
  };

  const testSummary = {
    content: 'Test summary',
    summaryType: 'abstract',
    toolAgent: 'test-agent',
    confidence_score: 0.95
  };

  beforeAll(async () => {
    // Initialize test database connection
    connectionManager = PostgresConnectionManager.getInstance({
      host: process.env.TEST_DB_HOST || 'localhost',
      port: parseInt(process.env.TEST_DB_PORT || '5432'),
      database: process.env.TEST_DB_NAME || 'test_docmanager',
      username: process.env.TEST_DB_USER || 'test_user',
      password: process.env.TEST_DB_PASSWORD || 'test_password'
    });
    
    connection = await connectionManager.getConnection();
    repository = new PostgresDocumentRepository(connection);
  });

  beforeEach(async () => {
    // Clean test data
    await connection.query('TRUNCATE documents CASCADE');
    await connection.query('TRUNCATE summaries CASCADE');
    await connection.query('TRUNCATE graph_nodes CASCADE');
    await connection.query('TRUNCATE graph_relationships CASCADE');
  });

  afterAll(async () => {
    await connectionManager.closeConnection();
  });

  describe('Basic CRUD Operations', () => {
    it('should create a new document', async () => {
      const result = await repository.create(testDoc);
      expect(result).toHaveProperty('id');
      expect(result.title).toBe(testDoc.title);
    });

    it('should find document by id', async () => {
      const created = await repository.create(testDoc);
      const found = await repository.findById(created.id);
      expect(found).toBeTruthy();
      expect(found?.title).toBe(testDoc.title);
    });

    it('should update document', async () => {
      const created = await repository.create(testDoc);
      const updated = await repository.update(created.id, {
        title: 'Updated Title'
      });
      expect(updated.title).toBe('Updated Title');
      expect(updated.version).toBe(created.version + 1);
    });

    it('should delete document', async () => {
      const created = await repository.create(testDoc);
      const deleted = await repository.delete(created.id);
      expect(deleted).toBe(true);
      const found = await repository.findById(created.id);
      expect(found).toBeNull();
    });
  });

  describe('Organization-specific Operations', () => {
    it('should find documents by organization', async () => {
      // Create test documents for different organizations
      await repository.create({ ...testDoc, orgId: 1 });
      await repository.create({ ...testDoc, orgId: 1 });
      await repository.create({ ...testDoc, orgId: 2 });

      const docs = await repository.findByOrganization(1);
      expect(docs).toHaveLength(2);
      expect(docs[0].orgId).toBe(1);
    });

    it('should support pagination in organization queries', async () => {
      // Create multiple test documents
      for (let i = 0; i < 15; i++) {
        await repository.create({ ...testDoc, orgId: 1, title: `Doc ${i}` });
      }

      const docs = await repository.findByOrganization(1, {
        limit: 10,
        offset: 5
      });
      expect(docs).toHaveLength(10);
    });
  });

  describe('Complex Operations', () => {
    it('should create document with summary', async () => {
      const result = await repository.createWithSummary(testDoc, testSummary);
      expect(result).toHaveProperty('id');
      
      // Verify summary was created
      const summaries = await connection.query(
        'SELECT * FROM summaries WHERE document_id = $1',
        [result.id]
      );
      expect(summaries).toHaveLength(1);
      expect(summaries[0].content).toBe(testSummary.content);
    });

    it('should handle version control when updating', async () => {
      const doc = await repository.create(testDoc);
      const updated = await repository.updateWithVersion(
        doc.id,
        { title: 'New Version' },
        'Updated title'
      );

      // Verify version was incremented
      expect(updated.version).toBe(doc.version + 1);

      // Verify version history was created
      const versions = await connection.query(
        'SELECT * FROM document_versions WHERE document_id = $1',
        [doc.id]
      );
      expect(versions).toHaveLength(1);
      expect(versions[0].title).toBe(doc.title);
    });

    it('should find related documents', async () => {
      // Create test documents and relationships
      const doc1 = await repository.create(testDoc);
      const doc2 = await repository.create({ ...testDoc, title: 'Related Doc' });

      // Create graph nodes
      await connection.query(`
        INSERT INTO graph_nodes (document_id, node_type, name, created_by_tool)
        VALUES ($1, 'document', 'Doc 1', 'test'), ($2, 'document', 'Doc 2', 'test')
      `, [doc1.id, doc2.id]);

      // Create relationship
      await connection.query(`
        INSERT INTO graph_relationships (
          source_node_id, target_node_id, relationship_type, created_by_tool
        )
        SELECT n1.id, n2.id, 'related_to', 'test'
        FROM graph_nodes n1, graph_nodes n2
        WHERE n1.document_id = $1 AND n2.document_id = $2
      `, [doc1.id, doc2.id]);

      const related = await repository.findRelatedDocuments(doc1.id);
      expect(related).toHaveLength(1);
      expect(related[0].id).toBe(doc2.id);
    });
  });

  describe('Error Handling', () => {
    it('should handle duplicate key violations', async () => {
      // Create document with unique external reference
      await repository.create({
        ...testDoc,
        externalRefId: 'unique-ref'
      });

      // Attempt to create another document with same reference
      await expect(repository.create({
        ...testDoc,
        externalRefId: 'unique-ref'
      })).rejects.toThrow('Duplicate entry detected');
    });

    it('should handle foreign key violations', async () => {
      await expect(repository.create({
        ...testDoc,
        ownerId: 999999, // Non-existent user
      })).rejects.toThrow('Referenced record does not exist');
    });

    it('should rollback transaction on error', async () => {
      const doc = await repository.create(testDoc);
      
      // Attempt operation that should fail and rollback
      try {
        await repository.createWithSummary(
          { ...testDoc, ownerId: 999999 }, // Will fail
          testSummary
        );
      } catch (error) {
        // Verify no partial changes were made
        const summaries = await connection.query(
          'SELECT * FROM summaries WHERE document_id = $1',
          [doc.id]
        );
        expect(summaries).toHaveLength(0);
      }
    });
  });
});
