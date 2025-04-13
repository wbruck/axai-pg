import { ConnectionOptions } from 'typeorm';

export interface PostgresConnectionConfig {
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
  schema?: string;
  ssl?: boolean;
}

export interface PostgresPoolConfig {
  min: number;
  max: number;
  idleTimeoutMs: number;
  acquireTimeoutMs: number;
}

export class PostgresConfig {
  private static DEFAULT_POOL_CONFIG: PostgresPoolConfig = {
    min: 2,
    max: 20,  // Suitable for dozens of concurrent users
    idleTimeoutMs: 30000,
    acquireTimeoutMs: 5000
  };

  static createConnectionOptions(
    connection: PostgresConnectionConfig,
    pool: Partial<PostgresPoolConfig> = {}
  ): ConnectionOptions {
    const poolConfig = { ...this.DEFAULT_POOL_CONFIG, ...pool };

    return {
      type: 'postgres',
      host: connection.host,
      port: connection.port,
      database: connection.database,
      username: connection.username,
      password: connection.password,
      schema: connection.schema || 'public',
      ssl: connection.ssl,
      
      // Connection pool configuration
      extra: {
        max: poolConfig.max,
        min: poolConfig.min,
        idleTimeoutMillis: poolConfig.idleTimeoutMs,
        acquireTimeoutMillis: poolConfig.acquireTimeoutMs
      },

      // Performance and reliability settings
      connectTimeoutMS: 10000,
      maxQueryExecutionTime: 1000, // Log slow queries (>1s)
      logging: ['error', 'warn', 'schema'],
      
      // Entity configuration
      entities: ['src/data/entities/**/*.ts'],
      synchronize: false, // Disable automatic schema sync
      
      // Cache configuration
      cache: {
        duration: 60000, // 1 minute cache
        type: 'database',
        tableName: 'query_cache'
      }
    };
  }

  static createPoolConfig(config: Partial<PostgresPoolConfig> = {}): PostgresPoolConfig {
    return { ...this.DEFAULT_POOL_CONFIG, ...config };
  }

  static validateConfig(config: PostgresConnectionConfig): void {
    if (!config.host) throw new Error('Database host is required');
    if (!config.database) throw new Error('Database name is required');
    if (!config.username) throw new Error('Database username is required');
    if (!config.password) throw new Error('Database password is required');
    if (config.port && (config.port < 1 || config.port > 65535)) {
      throw new Error('Invalid port number');
    }
  }
}
