from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint, CheckConstraint, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..config.database import Base

class Role(Base):
    """
    Role definitions with normalized role management.

    From market-ui integration - defines available roles in the system
    with descriptions and optional legacy permissions field.
    """
    __tablename__ = 'roles'

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Core Fields
    name = Column(Text, nullable=False, unique=True)
    description = Column(Text)
    permissions = Column(Text)  # Legacy comma-separated permissions

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    user_roles = relationship("UserRole", back_populates="role", lazy="dynamic")

    # Table Constraints
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="roles_name_not_empty"),
        Index('idx_roles_name', 'name'),
    )

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"

class UserRole(Base):
    """
    Model for user role assignments.

    Updated to reference Role table via role_id for normalized role management.
    Maintains backward compatibility with role_name field.
    """
    __tablename__ = 'user_roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    role_name = Column(Text, nullable=False)  # Legacy field for backward compatibility
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    assigner = relationship("User", foreign_keys=[assigned_by])
    role = relationship("Role", back_populates="user_roles")

    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
        Index('idx_user_roles_user_id', 'user_id'),
        Index('idx_user_roles_role_id', 'role_id'),
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

class AuditLog(Base):
    """
    Unified audit logging (merged from AccessLog).

    Renamed fields for clarity and consistency with market-ui:
    - action_type → action
    - table_affected → resource_type
    - record_id → resource_id
    - details: Text → JSON for structured data
    Added user_id FK in addition to username for better referential integrity.
    """
    __tablename__ = 'audit_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    username = Column(Text, nullable=False)
    action = Column(Text, nullable=False)
    action_time = Column(DateTime(timezone=True), server_default=func.now())
    resource_type = Column(Text, nullable=False)
    resource_id = Column(UUID(as_uuid=True))  # Can reference records from different tables
    details = Column(JSON)  # Changed from Text to JSON for structured logging

    # Relationships
    user = relationship("User")

    # Table Constraints
    __table_args__ = (
        Index('idx_audit_logs_user_id', 'user_id'),
        Index('idx_audit_logs_action_time', 'action_time'),
        Index('idx_audit_logs_resource_type', 'resource_type'),
    )

    def __repr__(self):
        return f"<AuditLog(id={self.id}, username='{self.username}', action='{self.action}')>"

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
