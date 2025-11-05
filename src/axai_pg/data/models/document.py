from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..config.database import Base

class Document(Base):
    """
    Core document storage with ownership and metadata.

    Documents are owned by users and belong to organizations (multi-tenant).
    They support versioning, summaries, topics, and graph relationships.
    """
    __tablename__ = 'documents'

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Core Fields
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
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
    document_metadata = Column(JSONB, name='metadata')

    # Relationships
    owner = relationship("User", back_populates="owned_documents")
    organization = relationship("Organization", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document", lazy="dynamic", cascade="all, delete-orphan")
    summaries = relationship("Summary", back_populates="document", lazy="dynamic", cascade="all, delete-orphan")
    topics = relationship("DocumentTopic", back_populates="document", lazy="dynamic", cascade="all, delete-orphan")
    graph_node = relationship("GraphNode", back_populates="document", uselist=False, cascade="all, delete-orphan")
    graph_relationships = relationship("GraphRelationship", back_populates="document", lazy="dynamic", cascade="all, delete-orphan")

    # Table Constraints
    __table_args__ = (
        CheckConstraint("length(trim(title)) > 0", name="documents_title_not_empty"),
        CheckConstraint(
            "status IN ('draft', 'published', 'archived', 'deleted')",
            name="documents_valid_status"
        ),
        CheckConstraint("version > 0", name="documents_valid_version"),
        CheckConstraint(
            "processing_status IN ('pending', 'processing', 'complete', 'error')",
            name="documents_valid_processing_status"
        ),
        Index('idx_documents_org_id', 'org_id'),
        Index('idx_documents_owner_id', 'owner_id'),
        Index('idx_documents_type', 'document_type'),
        Index('idx_documents_status', 'status'),
        Index('idx_documents_org_status', 'org_id', 'status'),
    )

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
