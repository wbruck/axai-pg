from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..config.database import Base

class User(Base):
    """Users belong to organizations and can own documents."""
    __tablename__ = 'users'

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Core Fields
    username = Column(Text, nullable=False, unique=True)
    email = Column(Text, nullable=False, unique=True)
    org_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="users")
    owned_documents = relationship("Document", back_populates="owner", lazy="dynamic")
    document_versions = relationship("DocumentVersion", back_populates="modified_by", lazy="dynamic")

    # Table Constraints - SQLAlchemy will read these from the DB
    __table_args__ = (
        # Check constraints are handled by PostgreSQL
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', org_id={self.org_id})>"
