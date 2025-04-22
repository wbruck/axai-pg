import { Connection, Repository, QueryRunner } from 'typeorm';
import { IDocumentRepository, Document, DocumentQueryOptions } from '../interfaces/IDocumentRepository';
import { QueryFailedError } from 'typeorm';

export class PostgresDocumentRepository implements IDocumentRepository {
  private repository: Repository<Document>;
  private connection: Connection;

  constructor(connection: Connection) {
    this.connection = connection;
    this.repository = connection.getRepository(Document);
  }

  async findById(id: number): Promise<Document | null> {
    try {
      const doc = await this.repository.findOne({
        where: { id },
        relations: ['summaries', 'topics']
      });
      return doc || null;
    } catch (error) {
      this.handleError(error);
      return null;
    }
  }

  async findByOrganization(orgId: number, options?: DocumentQueryOptions): Promise<Document[]> {
    try {
      const query = this.repository.createQueryBuilder('document')
        .where('document.orgId = :orgId', { orgId })
        .take(options?.limit || 50)
        .skip(options?.offset || 0);

      if (options?.includeSummaries) {
        query.leftJoinAndSelect('document.summaries', 'summary');
      }

      if (options?.includeTopics) {
        query.leftJoinAndSelect('document.topics', 'topic');
      }

      if (options?.orderBy) {
        Object.entries(options.orderBy).forEach(([key, order]) => {
          query.addOrderBy(`document.${key}`, order);
        });
      } else {
        query.orderBy('document.createdAt', 'DESC');
      }

      return await query.getMany();
    } catch (error) {
      this.handleError(error);
      return [];
    }
  }

  async findRelatedDocuments(documentId: number, maxDepth: number = 3): Promise<Document[]> {
    try {
      // Using recursive CTE for graph traversal
      const result = await this.connection.query(`
        WITH RECURSIVE related_docs(node_id, depth) AS (
          -- Base case: direct relationships
          SELECT target_node_id, 1
          FROM graph_relationships gr
          JOIN graph_nodes gn ON gr.source_node_id = gn.id
          WHERE gn.document_id = $1 AND gr.is_active = true
          
          UNION
          
          -- Recursive case: traverse graph
          SELECT gr.target_node_id, rd.depth + 1
          FROM graph_relationships gr
          JOIN related_docs rd ON gr.source_node_id = rd.node_id
          WHERE rd.depth < $2 AND gr.is_active = true
        )
        SELECT DISTINCT d.*
        FROM documents d
        JOIN graph_nodes gn ON d.id = gn.document_id
        JOIN related_docs rd ON gn.id = rd.node_id
        WHERE d.id != $1
        ORDER BY d.created_at DESC
      `, [documentId, maxDepth]);

      return result;
    } catch (error) {
      this.handleError(error);
      return [];
    }
  }

  async createWithSummary(document: Omit<Document, 'id'>, summary: any): Promise<Document> {
    const queryRunner = this.connection.createQueryRunner();
    await queryRunner.connect();
    await queryRunner.startTransaction();

    try {
      // Create document
      const newDocument = await queryRunner.manager.save(Document, document);

      // Create summary
      await queryRunner.manager.save('summaries', {
        ...summary,
        documentId: newDocument.id
      });

      await queryRunner.commitTransaction();
      return newDocument;
    } catch (error) {
      await queryRunner.rollbackTransaction();
      this.handleError(error);
      throw error;
    } finally {
      await queryRunner.release();
    }
  }

  async updateWithVersion(id: number, document: Partial<Document>, changeDescription?: string): Promise<Document> {
    const queryRunner = this.connection.createQueryRunner();
    await queryRunner.connect();
    await queryRunner.startTransaction();

    try {
      // Get current document
      const currentDoc = await queryRunner.manager.findOne(Document, id);
      if (!currentDoc) throw new Error('Document not found');

      // Create version record
      await queryRunner.manager.save('document_versions', {
        documentId: id,
        version: currentDoc.version,
        content: currentDoc.content,
        title: currentDoc.title,
        status: currentDoc.status,
        modifiedBy: document.ownerId,
        changeDescription
      });

      // Update document
      const updatedDoc = await queryRunner.manager.save(Document, {
        ...currentDoc,
        ...document,
        version: currentDoc.version + 1
      });

      await queryRunner.commitTransaction();
      return updatedDoc;
    } catch (error) {
      await queryRunner.rollbackTransaction();
      this.handleError(error);
      throw error;
    } finally {
      await queryRunner.release();
    }
  }

  private handleError(error: any): void {
    // Log error details
    console.error('Database operation failed:', error);

    if (error instanceof QueryFailedError) {
      // Handle specific PostgreSQL errors
      const pgError = error as any;
      switch (pgError.code) {
        case '23505': // unique_violation
          throw new Error('Duplicate entry detected');
        case '23503': // foreign_key_violation
          throw new Error('Referenced record does not exist');
        default:
          throw new Error('Database operation failed');
      }
    }

    throw error;
  }

  // Implement other IDocumentRepository methods...
}
