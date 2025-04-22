from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..config.database import Base

class Organization(Base):
    """Organizations represent B2B tenants in the multi-tenant system."""
    __tablename__ = 'organizations'

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Core Fields
    name = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="organization", lazy="dynamic")
    documents = relationship("Document", back_populates="organization", lazy="dynamic")

    # Table Constraints - SQLAlchemy will read these from the DB
    __table_args__ = (
        # Check constraints are handled by PostgreSQL
    )

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}')>"
