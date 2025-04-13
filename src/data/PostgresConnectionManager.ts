import { Connection, createConnection, getConnection } from 'typeorm';
import { PostgresConfig, PostgresConnectionConfig, PostgresPoolConfig } from './config/PostgresConfig';

export class PostgresConnectionManager {
  private static instance: PostgresConnectionManager;
  private connection: Connection | null = null;
  private connectionConfig: PostgresConnectionConfig;
  private poolConfig: PostgresPoolConfig;

  private constructor(
    connectionConfig: PostgresConnectionConfig,
    poolConfig?: Partial<PostgresPoolConfig>
  ) {
    this.connectionConfig = connectionConfig;
    this.poolConfig = PostgresConfig.createPoolConfig(poolConfig);
    PostgresConfig.validateConfig(connectionConfig);
  }

  static getInstance(
    connectionConfig?: PostgresConnectionConfig,
    poolConfig?: Partial<PostgresPoolConfig>
  ): PostgresConnectionManager {
    if (!PostgresConnectionManager.instance) {
      if (!connectionConfig) {
        throw new Error('Connection configuration required for initial setup');
      }
      PostgresConnectionManager.instance = new PostgresConnectionManager(connectionConfig, poolConfig);
    }
    return PostgresConnectionManager.instance;
  }

  async getConnection(): Promise<Connection> {
    try {
      // Try to get existing connection
      if (this.connection?.isConnected) {
        return this.connection;
      }

      // Try to get connection from TypeORM
      try {
        this.connection = getConnection();
        if (this.connection.isConnected) {
          return this.connection;
        }
      } catch (error) {
        // Connection doesn't exist, create new one below
      }

      // Create new connection
      this.connection = await createConnection(
        PostgresConfig.createConnectionOptions(this.connectionConfig, this.poolConfig)
      );

      return this.connection;
    } catch (error) {
      console.error('Failed to establish database connection:', error);
      throw new Error('Database connection failed');
    }
  }

  async closeConnection(): Promise<void> {
    if (this.connection?.isConnected) {
      await this.connection.close();
      this.connection = null;
    }
  }

  async executeInTransaction<T>(
    operation: (connection: Connection) => Promise<T>
  ): Promise<T> {
    const connection = await this.getConnection();
    const queryRunner = connection.createQueryRunner();
    await queryRunner.connect();
    await queryRunner.startTransaction();

    try {
      const result = await operation(connection);
      await queryRunner.commitTransaction();
      return result;
    } catch (error) {
      await queryRunner.rollbackTransaction();
      throw error;
    } finally {
      await queryRunner.release();
    }
  }

  async checkConnection(): Promise<boolean> {
    try {
      const connection = await this.getConnection();
      // Execute simple query to verify connection
      await connection.query('SELECT 1');
      return true;
    } catch (error) {
      console.error('Connection check failed:', error);
      return false;
    }
  }

  async getConnectionMetrics(): Promise<{
    active: number;
    idle: number;
    waiting: number;
  }> {
    try {
      const connection = await this.getConnection();
      const result = await connection.query(`
        SELECT 
          count(*) filter (where state = 'active') as active,
          count(*) filter (where state = 'idle') as idle,
          count(*) filter (where wait_event is not null) as waiting
        FROM pg_stat_activity 
        WHERE datname = $1
      `, [this.connectionConfig.database]);
      
      return result[0];
    } catch (error) {
      console.error('Failed to get connection metrics:', error);
      throw new Error('Could not retrieve connection metrics');
    }
  }
}
