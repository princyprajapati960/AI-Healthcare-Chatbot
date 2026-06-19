"""
Enhanced database schemas for comprehensive chatbot enhancements.
Includes medical knowledge base, medications, and audit logging tables.
Supports requirements: 2.1, 16.4, 18.1, 21.2, 21.3
"""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CHAR,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    TIMESTAMP,
    UUID,
)
from sqlalchemy.dialects.postgresql import ARRAY, INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.connection import Base


class MedicalCondition(Base):
    """
    Medical conditions knowledge base with symptoms, causes, and treatments.
    Requirements: 2.1 - Store 500+ medical conditions with comprehensive information
    """

    __tablename__ = "medical_conditions"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    icd10_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, index=True)
    
    # Using ARRAY for PostgreSQL - symptoms stored as text array for GIN indexing
    symptoms: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False)
    causes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    treatments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Citation sources for HIPAA compliance and information verification
    sources: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=True)
    
    # Track information freshness (Requirement 2.3)
    last_updated: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        nullable=False, 
        default=datetime.utcnow
    )
    review_required: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        nullable=False, 
        default=datetime.utcnow
    )

    # GIN index on symptoms array for fast full-text search (Requirement 21.2)
    __table_args__ = (
        Index('idx_conditions_symptoms_gin', 'symptoms', postgresql_using='gin'),
        Index('idx_conditions_updated', 'last_updated'),
    )


class Medication(Base):
    """
    Medications database with contraindications and drug interactions.
    Requirements: 3.2 - Check contraindications against user allergies
    """

    __tablename__ = "medications"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    generic_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Contraindications stored as array of condition/allergy names
    contraindications: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=True)
    side_effects: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=True)
    
    # Drug-drug interactions stored as array of medication IDs
    interactions: Mapped[Optional[str]] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=True)
    
    # Additional information
    dosage_forms: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=True)
    pregnancy_category: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        nullable=False, 
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        nullable=False, 
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    __table_args__ = (
        Index('idx_medications_name', 'name'),
        Index('idx_medications_generic', 'generic_name'),
    )


class AuditLog(Base):
    """
    Comprehensive audit logging for HIPAA compliance.
    Requirements: 16.4, 18.1, 18.2, 18.3, 18.4 - Log all security-relevant events
    
    Write-once constraint ensures immutability of audit records.
    """

    __tablename__ = "audit_logs"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Timestamp with timezone for accurate audit trail
    timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        nullable=False, 
        default=datetime.utcnow,
        index=True
    )
    
    # User identification
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    
    # Event classification
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Event types: 'auth_login', 'auth_logout', 'auth_failed', 'data_read', 
    # 'data_create', 'data_update', 'data_delete', 'config_change', 'api_request'
    
    resource: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    action: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Request metadata
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    request_params: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Configuration change tracking (Requirement 18.3)
    before_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    after_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Tamper detection (Requirement 18.5)
    hash: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    # SHA-256 hash computed over: timestamp + user_id + event_type + resource + action
    
    # Write-once constraint - prevents modification of audit records
    # This is enforced at application level and through database permissions
    # In PostgreSQL, use: GRANT INSERT ON audit_logs TO app_user;
    # REVOKE UPDATE, DELETE ON audit_logs FROM app_user;

    __table_args__ = (
        Index('idx_audit_timestamp', 'timestamp'),
        Index('idx_audit_user', 'user_id'),
        Index('idx_audit_event', 'event_type'),
        Index('idx_audit_resource', 'resource'),
        # Composite index for common queries filtering by user and time range
        Index('idx_audit_user_time', 'user_id', 'timestamp'),
    )


# Enhanced indexes on existing tables for query optimization (Requirement 21.2, 21.3)

# Add index to ChatMessage table for optimized queries
# These would be added via Alembic migration in production:
"""
CREATE INDEX idx_messages_session_time ON chat_messages(session_id, created_at DESC);
CREATE INDEX idx_messages_timestamp ON chat_messages(created_at DESC);
CREATE INDEX idx_sessions_user_active ON chat_sessions(user_id, is_active);
CREATE INDEX idx_sessions_user_started ON chat_sessions(user_id, started_at DESC);
"""
