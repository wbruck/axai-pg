from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..config.database import Base

class User(Base):
    """
    Users belong to organizations and can own documents.

    Each user is associated with exactly one organization (multi-tenant model).
    Users can own documents and create document versions.
    """
    __tablename__ = 'users'

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Core Fields
    username = Column(Text, nullable=False, unique=True)
    email = Column(Text, nullable=False, unique=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="users")
    owned_documents = relationship("Document", back_populates="owner", lazy="dynamic")
    document_versions = relationship("DocumentVersion", back_populates="modified_by", lazy="dynamic")

    # Table Constraints
    __table_args__ = (
        CheckConstraint("length(trim(username)) > 0", name="users_username_not_empty"),
        CheckConstraint(
            "email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'",
            name="users_email_valid"
        ),
        Index('idx_users_username', 'username'),
        Index('idx_users_email', 'email'),
        Index('idx_users_org_id', 'org_id'),
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', org_id={self.org_id})>"
