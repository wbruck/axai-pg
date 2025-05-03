import { IDocumentRepository } from './interfaces/IDocumentRepository';
import { PostgresDocumentRepository } from './repositories/PostgresDocumentRepository';
import { PostgresConnectionManager } from './PostgresConnectionManager';
import { Connection } from 'typeorm';

interface RepositoryMetrics {
  operationCount: number;
  errorCount: number;
  slowQueryCount: number;
  lastOperationTime: Date | null;
}

export class DataAccessFactory {
  private static instance: DataAccessFactory;
  private connectionManager: PostgresConnectionManager;
  private repositories: Map<string, any> = new Map();
  private metrics: Map<string, RepositoryMetrics> = new Map();

  private constructor(connectionManager: PostgresConnectionManager) {
    this.connectionManager = connectionManager;
  }

  static getInstance(connectionManager: PostgresConnectionManager): DataAccessFactory {
    if (!DataAccessFactory.instance) {
      DataAccessFactory.instance = new DataAccessFactory(connectionManager);
    }
    return DataAccessFactory.instance;
  }

  async getDocumentRepository(): Promise<IDocumentRepository> {
    const repoKey = 'document';
    
    if (!this.repositories.has(repoKey)) {
      const connection = await this.connectionManager.getConnection();
      const repository = this.createDocumentRepository(connection);
      this.repositories.set(repoKey, repository);
      this.initializeMetrics(repoKey);
    }

    return this.repositories.get(repoKey);
  }

  private createDocumentRepository(connection: Connection): IDocumentRepository {
    const repository = new PostgresDocumentRepository(connection);
    return this.wrapWithLoggingAndMetrics(repository, 'document');
  }

  private wrapWithLoggingAndMetrics<T extends object>(
    repository: T,
    repoName: string
  ): T {
    const metrics = this.metrics.get(repoName)!;
    const handler: ProxyHandler<T> = {
      get: (target: any, prop: string) => {
        const originalMethod = target[prop];
        if (typeof originalMethod === 'function') {
          return async (...args: any[]) => {
            const startTime = Date.now();
            try {
              metrics.operationCount++;
              metrics.lastOperationTime = new Date();
              const result = await originalMethod.apply(target, args);
              
              // Check for slow queries (>1s)
              const duration = Date.now() - startTime;
              if (duration > 1000) {
                metrics.slowQueryCount++;
                console.warn(`Slow query detected in ${repoName}.${prop}: ${duration}ms`);
              }
              
              return result;
            } catch (error) {
              metrics.errorCount++;
              console.error(`Error in ${repoName}.${prop}:`, error);
              throw error;
            }
          };
        }
        return originalMethod;
      }
    };

    return new Proxy(repository, handler);
  }

  private initializeMetrics(repoName: string): void {
    this.metrics.set(repoName, {
      operationCount: 0,
      errorCount: 0,
      slowQueryCount: 0,
      lastOperationTime: null
    });
  }

  getMetrics(repoName: string): RepositoryMetrics | null {
    return this.metrics.get(repoName) || null;
  }

  async getAllMetrics(): Promise<Record<string, RepositoryMetrics>> {
    const allMetrics: Record<string, RepositoryMetrics> = {};
    for (const [name, metrics] of this.metrics.entries()) {
      allMetrics[name] = { ...metrics };
    }
    return allMetrics;
  }

  async resetMetrics(repoName?: string): Promise<void> {
    if (repoName) {
      this.initializeMetrics(repoName);
    } else {
      this.metrics.forEach((_, name) => this.initializeMetrics(name));
    }
  }

  async closeAllConnections(): Promise<void> {
    this.repositories.clear();
    this.metrics.clear();
    await this.connectionManager.closeConnection();
  }
}
