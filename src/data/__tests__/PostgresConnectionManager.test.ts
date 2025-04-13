import { PostgresConnectionManager } from '../PostgresConnectionManager';
import { DataAccessFactory } from '../DataAccessFactory';
import { QueryFailedError } from 'typeorm';

describe('PostgresConnectionManager and DataAccessFactory', () => {
  let connectionManager: PostgresConnectionManager;
  let dataAccessFactory: DataAccessFactory;

  beforeAll(() => {
    connectionManager = PostgresConnectionManager.getInstance({
      host: process.env.TEST_DB_HOST || 'localhost',
      port: parseInt(process.env.TEST_DB_PORT || '5432'),
      database: process.env.TEST_DB_NAME || 'test_docmanager',
      username: process.env.TEST_DB_USER || 'test_user',
      password: process.env.TEST_DB_PASSWORD || 'test_password'
    });
    dataAccessFactory = DataAccessFactory.getInstance(connectionManager);
  });

  afterAll(async () => {
    await connectionManager.closeConnection();
  });

  describe('Connection Management', () => {
    it('should establish database connection', async () => {
      const connection = await connectionManager.getConnection();
      expect(connection.isConnected).toBe(true);
    });

    it('should reuse existing connection', async () => {
      const connection1 = await connectionManager.getConnection();
      const connection2 = await connectionManager.getConnection();
      expect(connection1).toBe(connection2);
    });

    it('should handle connection failures gracefully', async () => {
      // Create new instance with invalid credentials
      const badConnectionManager = PostgresConnectionManager.getInstance({
        host: 'invalid-host',
        port: 5432,
        database: 'invalid-db',
        username: 'invalid-user',
        password: 'invalid-password'
      }, undefined, true); // Force new instance

      await expect(badConnectionManager.getConnection())
        .rejects.toThrow('Database connection failed');
    });

    it('should check connection health', async () => {
      const isHealthy = await connectionManager.checkConnection();
      expect(isHealthy).toBe(true);
    });

    it('should provide connection metrics', async () => {
      const metrics = await connectionManager.getConnectionMetrics();
      expect(metrics).toHaveProperty('active');
      expect(metrics).toHaveProperty('idle');
      expect(metrics).toHaveProperty('waiting');
    });
  });

  describe('Transaction Management', () => {
    it('should execute operations in transaction', async () => {
      const result = await connectionManager.executeInTransaction(async (connection) => {
        // Perform test operation
        await connection.query('SELECT 1');
        return 'success';
      });
      expect(result).toBe('success');
    });

    it('should rollback transaction on error', async () => {
      // Create test table
      const connection = await connectionManager.getConnection();
      await connection.query(`
        CREATE TABLE IF NOT EXISTS test_transactions (
          id SERIAL PRIMARY KEY,
          value TEXT NOT NULL
        )
      `);

      try {
        await connectionManager.executeInTransaction(async (connection) => {
          // Insert valid record
          await connection.query(
            'INSERT INTO test_transactions (value) VALUES ($1)',
            ['test1']
          );

          // Force error with duplicate primary key
          await connection.query(
            'INSERT INTO test_transactions (id, value) VALUES (1, $1)',
            ['test2']
          );
        });
      } catch (error) {
        // Verify no records were inserted (transaction rolled back)
        const result = await connection.query('SELECT COUNT(*) FROM test_transactions');
        expect(parseInt(result[0].count)).toBe(0);
      }

      // Clean up
      await connection.query('DROP TABLE test_transactions');
    });
  });

  describe('DataAccessFactory', () => {
    it('should create and cache repository instances', async () => {
      const repo1 = await dataAccessFactory.getDocumentRepository();
      const repo2 = await dataAccessFactory.getDocumentRepository();
      expect(repo1).toBe(repo2);
    });

    it('should track repository metrics', async () => {
      const repo = await dataAccessFactory.getDocumentRepository();
      
      // Perform some operations
      try {
        await repo.findById(1);
        await repo.findByOrganization(1);
      } catch (error) {
        // Ignore errors for metric testing
      }

      const metrics = dataAccessFactory.getMetrics('document');
      expect(metrics?.operationCount).toBeGreaterThan(0);
    });

    it('should detect slow queries', async () => {
      const repo = await dataAccessFactory.getDocumentRepository();
      
      // Force a slow query
      const connection = await connectionManager.getConnection();
      await connection.query('SELECT pg_sleep(1.1)'); // Sleep for 1.1 seconds

      const metrics = dataAccessFactory.getMetrics('document');
      expect(metrics?.slowQueryCount).toBeGreaterThan(0);
    });

    it('should reset metrics', async () => {
      const repo = await dataAccessFactory.getDocumentRepository();
      
      // Perform some operations
      try {
        await repo.findById(1);
      } catch (error) {
        // Ignore errors for metric testing
      }

      await dataAccessFactory.resetMetrics('document');
      const metrics = dataAccessFactory.getMetrics('document');
      expect(metrics?.operationCount).toBe(0);
      expect(metrics?.errorCount).toBe(0);
      expect(metrics?.slowQueryCount).toBe(0);
    });

    it('should provide consolidated metrics', async () => {
      const repo = await dataAccessFactory.getDocumentRepository();
      
      // Perform some operations
      try {
        await repo.findById(1);
        await repo.findByOrganization(1);
      } catch (error) {
        // Ignore errors for metric testing
      }

      const allMetrics = await dataAccessFactory.getAllMetrics();
      expect(allMetrics).toHaveProperty('document');
      expect(allMetrics.document.operationCount).toBeGreaterThan(0);
    });
  });
});
