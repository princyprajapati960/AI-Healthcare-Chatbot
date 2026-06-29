"""
Enhanced database schemas for comprehensive chatbot enhancements.
Includes medical knowledge base, medications, and audit logging tables.
Supports requirements: 2.1, 16.4, 18.1, 21.2, 21.3

NOTE: Uses SQLite-compatible types. For PostgreSQL, consider using
ARRAY, JSONB, INET, and UUID types for better performance.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.connection import Base


class MedicalCondition(Base):
    """
    Medical conditions knowledge base with symptoms, causes, and treatments.
    Requirements: 2.1 - Store 500+ medical conditions with comprehensive information
    """

    __tablename__ = "medical_conditions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    icd10_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, index=True)
    
    # Symptoms stored as JSON string for SQLite compatibility
    symptoms: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    causes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    treatments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Citation sources stored as JSON string
    sources: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Track information freshness (Requirement 2.3)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow
    )
    review_required: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow
    )

    __table_args__ = (
        Index('idx_conditions_updated', 'last_updated'),
    )


class Medication(Base):
    """
    Medications database with contraindications and drug interactions.
    Requirements: 3.2 - Check contraindications against user allergies
    """

    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    generic_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Stored as JSON strings for SQLite compatibility
    contraindications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    side_effects: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    interactions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    dosage_forms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pregnancy_category: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
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
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow,
        index=True
    )
    
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    action: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Request metadata
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    request_params: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Configuration change tracking
    before_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    after_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Tamper detection hash
    hash: Mapped[str] = mapped_column(String(64), nullable=False, default="")

    __table_args__ = (
        Index('idx_audit_timestamp', 'timestamp'),
        Index('idx_audit_user', 'user_id'),
        Index('idx_audit_event', 'event_type'),
        Index('idx_audit_resource', 'resource'),
        Index('idx_audit_user_time', 'user_id', 'timestamp'),
    )
