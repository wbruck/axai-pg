import { IRepository, QueryOptions } from './IRepository';

export interface Document {
  id: number;
  title: string;
  content: string;
  ownerId: number;
  orgId: number;
  documentType: string;
  status: 'draft' | 'published' | 'archived' | 'deleted';
  version: number;
  createdAt: Date;
  updatedAt: Date;
  fileFormat?: string;
  sizeBytes?: number;
  wordCount?: number;
  processingStatus: 'pending' | 'processing' | 'complete' | 'error';
  source?: string;
  contentHash?: string;
  externalRefId?: string;
  metadata?: Record<string, any>;
}

export interface DocumentQueryOptions extends QueryOptions {
  includeContent?: boolean;
  includeSummaries?: boolean;
  includeTopics?: boolean;
}

export interface IDocumentRepository extends IRepository<Document> {
  // Organization-specific queries
  findByOrganization(orgId: number, options?: DocumentQueryOptions): Promise<Document[]>;
  findByOwner(ownerId: number, options?: DocumentQueryOptions): Promise<Document[]>;
  
  // Topic and relationship queries
  findByTopic(topicId: number, options?: DocumentQueryOptions): Promise<Document[]>;
  findRelatedDocuments(documentId: number, maxDepth?: number): Promise<Document[]>;
  
  // Document operations with associated data
  createWithSummary(document: Omit<Document, 'id'>, summary: any): Promise<Document>;
  updateWithVersion(id: number, document: Partial<Document>, changeDescription?: string): Promise<Document>;
  
  // Specialized queries
  search(query: string, orgId: number, options?: DocumentQueryOptions): Promise<Document[]>;
  findByStatus(status: Document['status'], orgId: number, options?: DocumentQueryOptions): Promise<Document[]>;
}
