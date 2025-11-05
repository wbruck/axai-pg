from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint, CheckConstraint, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..config.database import Base

class UserRole(Base):
    """Model for user role assignments."""
    __tablename__ = 'user_roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role_name = Column(Text, nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    assigner = relationship("User", foreign_keys=[assigned_by])
    
    __table_args__ = (
        UniqueConstraint('user_id', 'role_name', name='uq_user_role'),
    )

class RolePermission(Base):
    """Model for role-based permissions."""
    __tablename__ = 'role_permissions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name = Column(Text, nullable=False)
    resource_name = Column(Text, nullable=False)
    permission_type = Column(Text, nullable=False)
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    granted_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    granter = relationship("User", foreign_keys=[granted_by])
    
    __table_args__ = (
        CheckConstraint(
            "permission_type IN ('READ', 'CREATE', 'UPDATE', 'DELETE')",
            name='valid_permission_type'
        ),
        UniqueConstraint('role_name', 'resource_name', 'permission_type', 
                        name='uq_role_permission'),
    )

class AccessLog(Base):
    """Model for access audit logging."""
    __tablename__ = 'access_log'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(Text, nullable=False)
    action_type = Column(Text, nullable=False)
    action_time = Column(DateTime(timezone=True), server_default=func.now())
    table_affected = Column(Text, nullable=False)
    record_id = Column(UUID(as_uuid=True))  # Can reference records from different tables
    details = Column(Text)

class RateLimit(Base):
    """Model for rate limiting."""
    __tablename__ = 'rate_limits'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    action_type = Column(Text, nullable=False)
    window_start = Column(DateTime(timezone=True), server_default=func.now())
    count = Column(Integer, default=1)
    
    # Relationships
    user = relationship("User")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'action_type', 'window_start', 
                        name='uq_rate_limit'),
    )

class SecurityPolicy(Base):
    """Model for security policies."""
    __tablename__ = 'security_policies'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False, unique=True)
    description = Column(Text)
    policy_type = Column(Text, nullable=False)
    policy_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    
    __table_args__ = (
        CheckConstraint(
            "policy_type IN ('ACCESS_CONTROL', 'DATA_PROTECTION', 'AUDIT', 'RATE_LIMIT')",
            name='valid_policy_type'
        ),
    )
