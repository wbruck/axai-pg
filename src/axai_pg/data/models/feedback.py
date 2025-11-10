from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..config.database import Base

class Feedback(Base):
    """
    User feedback submission storage.

    From market-ui integration - captures user feedback with context.
    Supports both authenticated (user_id) and anonymous (user_email) feedback.
    """
    __tablename__ = 'feedback'

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Core Fields
    type = Column(Text, nullable=False)
    description = Column(Text, nullable=False)

    # Context and Metadata
    page_context = Column(JSON, nullable=True)

    # User Identification (one of these should be populated)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    user_email = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="feedback_submissions")

    # Table Constraints
    __table_args__ = (
        CheckConstraint("length(trim(type)) > 0", name="feedback_type_not_empty"),
        CheckConstraint("length(trim(description)) > 0", name="feedback_description_not_empty"),
        Index('idx_feedback_user_id', 'user_id'),
        Index('idx_feedback_type', 'type'),
        Index('idx_feedback_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<Feedback(id={self.id}, type='{self.type}', user_id={self.user_id})>"
