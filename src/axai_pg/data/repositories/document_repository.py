from typing import List, Optional, Dict, Any
from datetime import timedelta
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session, joinedload
from .base_repository import BaseRepository
from .cache_manager import cache_query
from .metrics_utils import track_metrics, with_metrics
from ..models.document import Document

@with_metrics
class DocumentRepository(BaseRepository[Document]):
    """Repository for managing Document entities with specialized document operations."""
    model_class = Document
    
    def __init__(self):
        super().__init__(Document)
    
    @cache_query(ttl=timedelta(minutes=15))
    @track_metrics(Document)
    async def find_by_organization(self, org_id: int, options: Optional[Dict[str, Any]] = None) -> List[Document]:
        try:
            with self._get_session() as session:
                query = session.query(Document).filter(Document.org_id == org_id)
                query = self._apply_document_options(query, options)
                return query.all()
        except Exception as e:
            raise RuntimeError(f"Error finding documents by organization: {str(e)}") from e
    
    @cache_query(ttl=timedelta(minutes=15))
    @track_metrics(Document)
    async def find_by_owner(self, owner_id: int, options: Optional[Dict[str, Any]] = None) -> List[Document]:
        try:
            with self._get_session() as session:
                query = session.query(Document).filter(Document.owner_id == owner_id)
                query = self._apply_document_options(query, options)
                return query.all()
        except Exception as e:
            raise RuntimeError(f"Error finding documents by owner: {str(e)}") from e
    
    @cache_query(ttl=timedelta(minutes=30))
    @track_metrics(Document)
    async def find_by_topic(self, topic_id: int, options: Optional[Dict[str, Any]] = None) -> List[Document]:
        try:
            with self._get_session() as session:
                query = session.query(Document)\
                    .join(DocumentTopic)\
                    .filter(DocumentTopic.topic_id == topic_id)
                query = self._apply_document_options(query, options)
                return query.all()
        except Exception as e:
            raise RuntimeError(f"Error finding documents by topic: {str(e)}") from e
    
    @cache_query(ttl=timedelta(minutes=30))
    @track_metrics(Document)
    async def find_related_documents(self, document_id: int, max_depth: int = 2) -> List[Document]:
        """Find related documents using graph relationships up to max_depth."""
        try:
            with self._get_session() as session:
                # This would use a recursive CTE query to traverse the graph
                query = """
                WITH RECURSIVE related_docs AS (
                    -- Base case: direct relationships
                    SELECT DISTINCT d.id, d.title, 1 as depth
                    FROM documents d
                    JOIN graph_relationships gr ON gr.source_id = :doc_id 
                        AND gr.target_id = d.id
                    WHERE d.id != :doc_id
                    
                    UNION
                    
                    -- Recursive case: traverse relationships
                    SELECT DISTINCT d.id, d.title, rd.depth + 1
                    FROM related_docs rd
                    JOIN graph_relationships gr ON gr.source_id = rd.id
                    JOIN documents d ON gr.target_id = d.id
                    WHERE d.id != :doc_id AND rd.depth < :max_depth
                )
                SELECT DISTINCT d.*
                FROM documents d
                JOIN related_docs rd ON rd.id = d.id
                ORDER BY rd.depth;
                """
                result = session.execute(query, {"doc_id": document_id, "max_depth": max_depth})
                return [Document(**row) for row in result]
        except Exception as e:
            raise RuntimeError(f"Error finding related documents: {str(e)}") from e
    
    @track_metrics(Document)
    async def create_with_summary(self, document: Dict[str, Any], summary: Dict[str, Any]) -> Document:
        """Create a document and its summary in a single transaction."""
        async def _create_both(session: Session):
            # Create document
            db_document = Document(**document)
            session.add(db_document)
            session.flush()  # Flush to get the document ID
            
            # Create summary with document reference
            summary['document_id'] = db_document.id
            db_summary = Summary(**summary)
            session.add(db_summary)
            
            return db_document
        
        return await self.transaction(_create_both)
    
    @track_metrics(Document)
    async def update_with_version(self, id: int, document: Dict[str, Any], change_description: Optional[str] = None) -> Document:
        """Update document while creating a new version record."""
        async def _update_with_version(session: Session):
            # Get current document
            current = session.query(Document).filter_by(id=id).first()
            if not current:
                raise ValueError(f"Document {id} not found")
            
            # Create version record
            version = {
                'document_id': id,
                'version': current.version + 1,
                'content': current.content,
                'title': current.title,
                'change_description': change_description
            }
            session.execute(
                'INSERT INTO document_versions (document_id, version, content, title, change_description) '
                'VALUES (:document_id, :version, :content, :title, :change_description)',
                version
            )
            
            # Update document
            for key, value in document.items():
                setattr(current, key, value)
            current.version += 1
            
            return current
        
        return await self.transaction(_update_with_version)
    
    @cache_query(ttl=timedelta(minutes=5))
    @track_metrics(Document)
    async def search(self, query: str, org_id: int, options: Optional[Dict[str, Any]] = None) -> List[Document]:
        """Search documents using full-text search capabilities."""
        try:
            with self._get_session() as session:
                search_query = session.query(Document)\
                    .filter(Document.org_id == org_id)\
                    .filter(
                        or_(
                            Document.title.ilike(f"%{query}%"),
                            Document.content.ilike(f"%{query}%")
                        )
                    )
                search_query = self._apply_document_options(search_query, options)
                return search_query.all()
        except Exception as e:
            raise RuntimeError(f"Error searching documents: {str(e)}") from e
    
    @cache_query(ttl=timedelta(minutes=15))
    @track_metrics(Document)
    async def find_by_status(self, status: str, org_id: int, options: Optional[Dict[str, Any]] = None) -> List[Document]:
        try:
            with self._get_session() as session:
                query = session.query(Document)\
                    .filter(Document.org_id == org_id)\
                    .filter(Document.status == status)
                query = self._apply_document_options(query, options)
                return query.all()
        except Exception as e:
            raise RuntimeError(f"Error finding documents by status: {str(e)}") from e
    
    def _apply_document_options(self, query, options: Optional[Dict[str, Any]] = None):
        """Apply document-specific query options."""
        if not options:
            return query
            
        if options.get('include_summaries'):
            query = query.options(joinedload(Document.summaries))
            
        if options.get('include_topics'):
            query = query.options(joinedload(Document.topics))
            
        if 'offset' in options:
            query = query.offset(options['offset'])
            
        if 'limit' in options:
            query = query.limit(options['limit'])
            
        if 'order_by' in options:
            for field, direction in options['order_by'].items():
                column = getattr(Document, field)
                if direction == 'DESC':
                    column = column.desc()
                query = query.order_by(column)
                
        return query
