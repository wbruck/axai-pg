export interface IRepository<T> {
  // Core CRUD operations
  findById(id: number): Promise<T | null>;
  findMany(criteria: Record<string, any>, options?: QueryOptions): Promise<T[]>;
  create(entity: Omit<T, 'id'>): Promise<T>;
  update(id: number, entity: Partial<T>): Promise<T>;
  delete(id: number): Promise<boolean>;
  
  // Transaction support
  transaction<R>(operation: (manager: any) => Promise<R>): Promise<R>;
}

export interface QueryOptions {
  offset?: number;
  limit?: number;
  orderBy?: Record<string, 'ASC' | 'DESC'>;
  include?: string[];
}
