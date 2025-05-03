from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..config.database import Base

class Document(Base):
    """Core document storage with ownership and metadata."""
    __tablename__ = 'documents'

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Core Fields
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    document_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default='draft')
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    file_format = Column(String(50))
    size_bytes = Column(Integer)
    word_count = Column(Integer)
    processing_status = Column(String(50), default='pending')
    source = Column(String(100))
    content_hash = Column(String(64))
    external_ref_id = Column(String(100))
    document_metadata = Column(JSON, name='metadata')

    # Relationships
    owner = relationship("User", back_populates="owned_documents")
    organization = relationship("Organization", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document", lazy="dynamic")
    summaries = relationship("Summary", back_populates="document", lazy="dynamic")
    topics = relationship("DocumentTopic", back_populates="document", lazy="dynamic")
    graph_node = relationship("GraphNode", back_populates="document", uselist=False)
    graph_relationships = relationship("GraphRelationship", back_populates="document", lazy="dynamic")

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', version={self.version})>"

class DocumentVersion(Base):
    """Historical versions of documents for version control."""
    __tablename__ = 'document_versions'

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Core Fields
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    status = Column(String(20), nullable=False)
    modified_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    change_description = Column(Text)
    doc_metadata = Column(JSON)

    # Relationships
    document = relationship("Document", back_populates="versions")
    modified_by = relationship("User", back_populates="document_versions")

    # Unique constraint for document_id and version combination
    __table_args__ = (
        CheckConstraint("version > 0", name="document_versions_valid_version"),
    )

    def __repr__(self):
        return f"<DocumentVersion(document_id={self.document_id}, version={self.version})>"
