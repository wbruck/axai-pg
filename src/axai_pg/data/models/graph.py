from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Numeric, Boolean, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..config.database import Base

class GraphNode(Base):
    """Nodes for the graph representation of document connections."""
    __tablename__ = 'graph_nodes'

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Core Fields
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='SET NULL'))
    node_type = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    properties = Column(JSON)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    created_by_tool = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    document = relationship("Document", back_populates="graph_node")
    outgoing_relationships = relationship("GraphRelationship", 
                                       foreign_keys="GraphRelationship.source_node_id",
                                       back_populates="source_node",
                                       lazy="dynamic")
    incoming_relationships = relationship("GraphRelationship", 
                                       foreign_keys="GraphRelationship.target_node_id",
                                       back_populates="target_node",
                                       lazy="dynamic")

    # Table Constraints
    __table_args__ = (
        CheckConstraint("node_type IN ('document', 'concept', 'entity', 'topic', 'user', 'custom')",
                       name="graph_nodes_valid_type"),
    )

    def __repr__(self):
        return f"<GraphNode(id={self.id}, type='{self.node_type}', name='{self.name}')>"

class GraphRelationship(Base):
    """Relationships between nodes in the document graph structure."""
    __tablename__ = 'graph_relationships'

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Core Fields
    source_node_id = Column(Integer, ForeignKey('graph_nodes.id', ondelete='CASCADE'), nullable=False)
    target_node_id = Column(Integer, ForeignKey('graph_nodes.id', ondelete='CASCADE'), nullable=False)
    relationship_type = Column(String(50), nullable=False)
    is_directed = Column(Boolean, nullable=False, default=True)
    weight = Column(Numeric(10, 5))
    confidence_score = Column(Numeric(5, 4))
    properties = Column(JSON)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    created_by_tool = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    source_node = relationship("GraphNode", foreign_keys=[source_node_id], back_populates="outgoing_relationships")
    target_node = relationship("GraphNode", foreign_keys=[target_node_id], back_populates="incoming_relationships")

    # Table Constraints
    __table_args__ = (
        CheckConstraint("confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
                       name="graph_relationships_valid_confidence"),
        CheckConstraint("weight IS NULL OR weight > 0",
                       name="graph_relationships_valid_weight"),
        CheckConstraint("relationship_type IN ('references', 'contains', 'related_to', 'similar_to', 'contradicts', 'supports', 'custom')",
                       name="graph_relationships_valid_type"),
    )

    def __repr__(self):
        return f"<GraphRelationship(id={self.id}, type='{self.relationship_type}', source={self.source_node_id}, target={self.target_node_id})>"
