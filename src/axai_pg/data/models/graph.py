from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Numeric, Boolean, CheckConstraint, Index, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from ..config.database import Base

class SourceType(enum.Enum):
    """Enum for entity/relationship source types"""
    file = "file"
    collection_generated = "collection_generated"
    document = "document"

class GraphEntity(Base):
    """
    Entities for graph representation of document connections.

    Renamed from GraphNode to GraphEntity. Entities can originate from files,
    collections, or documents, and are tracked with source metadata.
    """
    __tablename__ = 'graph_entities'

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Core Identity Fields (from market-ui)
    entity_id = Column(Text, nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)

    # Entity Data
    name = Column(String(255), nullable=False)
    description = Column(Text)
    properties = Column(JSON)

    # Source Tracking (from market-ui)
    source_type = Column(SQLEnum(SourceType), nullable=True)
    source_file_id = Column(UUID(as_uuid=True), ForeignKey('documents.id', ondelete='CASCADE'), nullable=True, index=True)
    source_collection_id = Column(UUID(as_uuid=True), ForeignKey('collections.id', ondelete='CASCADE'), nullable=True, index=True)

    # Legacy document relationship (nullable for non-document entities)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id', ondelete='SET NULL'), nullable=True)

    # Timestamps and Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    created_by_tool = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    document = relationship("Document", back_populates="graph_entity", foreign_keys=[document_id])
    source_file = relationship("Document", back_populates="graph_entities", foreign_keys=[source_file_id])
    source_collection = relationship("Collection", back_populates="graph_entities")
    entity_links = relationship("EntityLink", back_populates="graph_entity", lazy="dynamic", cascade="all, delete-orphan")
    outgoing_relationships = relationship("GraphRelationship",
                                       foreign_keys="GraphRelationship.source_entity_id",
                                       back_populates="source_entity",
                                       lazy="dynamic")
    incoming_relationships = relationship("GraphRelationship",
                                       foreign_keys="GraphRelationship.target_entity_id",
                                       back_populates="target_entity",
                                       lazy="dynamic")

    # Table Constraints
    __table_args__ = (
        Index('idx_graph_entities_entity_id', 'entity_id'),
        Index('idx_graph_entities_entity_type', 'entity_type'),
        Index('idx_graph_entities_source_file_id', 'source_file_id'),
        Index('idx_graph_entities_source_collection_id', 'source_collection_id'),
        Index('idx_graph_entities_document_id', 'document_id'),
    )

    def __repr__(self):
        return f"<GraphEntity(id={self.id}, entity_type='{self.entity_type}', name='{self.name}')>"

class GraphRelationship(Base):
    """
    Relationships between entities in the document graph structure.

    Updated to reference GraphEntity (formerly GraphNode).
    Supports source tracking from files, collections, or documents.
    """
    __tablename__ = 'graph_relationships'

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Core Fields (renamed from source_node_id/target_node_id)
    source_entity_id = Column(UUID(as_uuid=True), ForeignKey('graph_entities.id', ondelete='CASCADE'), nullable=False)
    target_entity_id = Column(UUID(as_uuid=True), ForeignKey('graph_entities.id', ondelete='CASCADE'), nullable=False)

    # Relationship Identity (from market-ui)
    relationship_id = Column(Text, nullable=True, index=True)
    relationship_type = Column(String(50), nullable=False)

    # Source Tracking (from market-ui)
    source_type = Column(SQLEnum(SourceType), nullable=True)
    source_file_id = Column(UUID(as_uuid=True), ForeignKey('documents.id', ondelete='CASCADE'), nullable=True, index=True)
    source_collection_id = Column(UUID(as_uuid=True), ForeignKey('collections.id', ondelete='CASCADE'), nullable=True, index=True)

    # Legacy document relationship (nullable for non-document relationships)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id', ondelete='SET NULL'), nullable=True)

    # Relationship Metadata
    is_directed = Column(Boolean, nullable=False, default=True)
    weight = Column(Numeric(10, 5))
    confidence_score = Column(Numeric(5, 4))
    properties = Column(JSON)

    # Timestamps and Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    created_by_tool = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    source_entity = relationship("GraphEntity", foreign_keys=[source_entity_id], back_populates="outgoing_relationships")
    target_entity = relationship("GraphEntity", foreign_keys=[target_entity_id], back_populates="incoming_relationships")
    document = relationship("Document", back_populates="graph_relationships_rel", foreign_keys=[document_id])
    source_file = relationship("Document", foreign_keys=[source_file_id], overlaps="graph_relationships_rel,document")
    source_collection = relationship("Collection", back_populates="graph_relationships")

    # Table Constraints
    __table_args__ = (
        CheckConstraint("confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
                       name="graph_relationships_valid_confidence"),
        CheckConstraint("weight IS NULL OR weight > 0",
                       name="graph_relationships_valid_weight"),
        Index('idx_graph_relationships_source_entity_id', 'source_entity_id'),
        Index('idx_graph_relationships_target_entity_id', 'target_entity_id'),
        Index('idx_graph_relationships_relationship_id', 'relationship_id'),
        Index('idx_graph_relationships_source_file_id', 'source_file_id'),
        Index('idx_graph_relationships_source_collection_id', 'source_collection_id'),
        Index('idx_graph_relationships_document_id', 'document_id'),
    )

    def __repr__(self):
        return f"<GraphRelationship(id={self.id}, type='{self.relationship_type}', source={self.source_entity_id}, target={self.target_entity_id})>"
