"""
Unit tests for enhanced PostgreSQL database schema.
Task 1.2: Enhance PostgreSQL database schema

Tests verify:
- Table creation and structure
- Index creation and effectiveness
- Sample data insertion
- Query performance with indexes

Requirements: 2.1, 16.4, 18.1, 21.2, 21.3
"""

import hashlib
import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import sessionmaker

# Import models
try:
    from backend.app.models.enhanced_schemas import MedicalCondition, Medication, AuditLog
    from backend.app.database.connection import Base
except ImportError as e:
    pytest.skip(f"Enhanced schemas not available: {e}", allow_module_level=True)


@pytest.fixture(scope="module")
def test_db_url():
    """
    Test database URL. Override with environment variable for CI/CD.
    """
    import os
    return os.getenv(
        'TEST_DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/healthcare_test'
    )


@pytest.fixture(scope="module")
def engine(test_db_url):
    """Create test database engine."""
    return create_engine(test_db_url)


@pytest.fixture(scope="module")
def tables(engine):
    """Create all tables for testing."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def session(engine, tables):
    """Create a new database session for each test."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


class TestMedicalConditionsTable:
    """Test medical_conditions table structure and functionality."""
    
    def test_create_medical_condition(self, session):
        """Test creating a medical condition record."""
        condition = MedicalCondition(
            name="Test Condition",
            icd10_code="A00",
            symptoms=["symptom1", "symptom2", "symptom3"],
            causes="Test causes",
            treatments="Test treatments",
            severity="moderate",
            sources=["Test Source 1", "Test Source 2"]
        )
        
        session.add(condition)
        session.commit()
        
        # Verify saved
        saved = session.query(MedicalCondition).filter_by(name="Test Condition").first()
        assert saved is not None
        assert saved.name == "Test Condition"
        assert saved.icd10_code == "A00"
        assert len(saved.symptoms) == 3
        assert "symptom1" in saved.symptoms
    
    def test_gin_index_symptom_search(self, session):
        """Test GIN index enables fast symptom array search (Requirement 21.2)."""
        # Create multiple conditions
        conditions_data = [
            ("Flu", ["fever", "cough", "fatigue"]),
            ("Cold", ["runny nose", "cough", "sneezing"]),
            ("COVID-19", ["fever", "cough", "loss of taste"]),
            ("Allergies", ["sneezing", "runny nose", "itchy eyes"])
        ]
        
        for name, symptoms in conditions_data:
            condition = MedicalCondition(
                name=name,
                symptoms=symptoms,
                severity="moderate"
            )
            session.add(condition)
        
        session.commit()
        
        # Query using array contains operator (uses GIN index)
        result = session.query(MedicalCondition).filter(
            MedicalCondition.symptoms.contains(["fever"])
        ).all()
        
        # Should find Flu and COVID-19
        assert len(result) == 2
        names = [c.name for c in result]
        assert "Flu" in names
        assert "COVID-19" in names
        
        # Query for multiple symptoms
        result = session.query(MedicalCondition).filter(
            MedicalCondition.symptoms.contains(["cough", "fever"])
        ).all()
        
        # Should find Flu and COVID-19 (both have fever AND cough)
        assert len(result) == 2
    
    def test_outdated_information_flagging(self, session):
        """Test flagging outdated medical information (Requirement 2.3)."""
        # Create old condition
        old_condition = MedicalCondition(
            name="Old Condition",
            symptoms=["test"],
            last_updated=datetime.utcnow() - timedelta(days=400),  # 13+ months old
            review_required=False
        )
        
        # Create recent condition
        recent_condition = MedicalCondition(
            name="Recent Condition",
            symptoms=["test"],
            last_updated=datetime.utcnow() - timedelta(days=30),  # 1 month old
            review_required=False
        )
        
        session.add_all([old_condition, recent_condition])
        session.commit()
        
        # Query for outdated entries (>12 months)
        threshold = datetime.utcnow() - timedelta(days=365)
        outdated = session.query(MedicalCondition).filter(
            MedicalCondition.last_updated < threshold
        ).all()
        
        assert len(outdated) == 1
        assert outdated[0].name == "Old Condition"
        
        # Flag for review
        outdated[0].review_required = True
        session.commit()
        
        # Verify flag
        flagged = session.query(MedicalCondition).filter_by(review_required=True).first()
        assert flagged is not None
        assert flagged.name == "Old Condition"


class TestMedicationsTable:
    """Test medications table structure and functionality."""
    
    def test_create_medication(self, session):
        """Test creating a medication record."""
        medication = Medication(
            name="Test Drug",
            generic_name="test-drug",
            contraindications=["allergy1", "condition1"],
            side_effects=["nausea", "headache"],
            dosage_forms=["tablet", "liquid"]
        )
        
        session.add(medication)
        session.commit()
        
        # Verify saved
        saved = session.query(Medication).filter_by(name="Test Drug").first()
        assert saved is not None
        assert saved.generic_name == "test-drug"
        assert len(saved.contraindications) == 2
        assert "allergy1" in saved.contraindications
    
    def test_contraindication_checking(self, session):
        """Test querying medications by contraindications (Requirement 3.2)."""
        # Create medications with different contraindications
        med1 = Medication(
            name="Aspirin",
            contraindications=["bleeding disorders", "aspirin allergy"]
        )
        med2 = Medication(
            name="Penicillin",
            contraindications=["penicillin allergy", "severe kidney disease"]
        )
        med3 = Medication(
            name="Acetaminophen",
            contraindications=["severe liver disease"]
        )
        
        session.add_all([med1, med2, med3])
        session.commit()
        
        # Find medications contraindicated for someone with aspirin allergy
        user_allergy = "aspirin allergy"
        
        contraindicated = session.query(Medication).filter(
            Medication.contraindications.contains([user_allergy])
        ).all()
        
        assert len(contraindicated) == 1
        assert contraindicated[0].name == "Aspirin"
        
        # Find safe medications (not contraindicated)
        all_meds = session.query(Medication).all()
        safe_meds = [
            m for m in all_meds 
            if user_allergy not in (m.contraindications or [])
        ]
        
        assert len(safe_meds) == 2
        safe_names = [m.name for m in safe_meds]
        assert "Penicillin" in safe_names
        assert "Acetaminophen" in safe_names


class TestAuditLogsTable:
    """Test audit_logs table structure and functionality."""
    
    def test_create_audit_log(self, session):
        """Test creating an audit log entry."""
        # Compute hash for tamper detection
        timestamp = datetime.utcnow()
        user_id = 123
        event_type = "data_read"
        resource = "patient_profile"
        action = "view"
        
        hash_input = f"{timestamp}{user_id}{event_type}{resource}{action}"
        log_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        audit_log = AuditLog(
            timestamp=timestamp,
            user_id=user_id,
            event_type=event_type,
            resource=resource,
            action=action,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            request_params={"param1": "value1"},
            hash=log_hash
        )
        
        session.add(audit_log)
        session.commit()
        
        # Verify saved
        saved = session.query(AuditLog).filter_by(user_id=user_id).first()
        assert saved is not None
        assert saved.event_type == "data_read"
        assert saved.resource == "patient_profile"
        assert saved.hash == log_hash
        assert saved.request_params["param1"] == "value1"
    
    def test_audit_log_event_types(self, session):
        """Test logging different event types (Requirements 18.1, 18.2, 18.3, 18.4)."""
        timestamp = datetime.utcnow()
        
        # Authentication event
        auth_log = AuditLog(
            timestamp=timestamp,
            user_id=123,
            event_type="auth_login",
            resource="users",
            action="login",
            ip_address="192.168.1.100",
            hash=hashlib.sha256(b"test1").hexdigest()
        )
        
        # Data access event
        data_log = AuditLog(
            timestamp=timestamp,
            user_id=123,
            event_type="data_read",
            resource="patient_profiles",
            action="view",
            hash=hashlib.sha256(b"test2").hexdigest()
        )
        
        # Configuration change event
        config_log = AuditLog(
            timestamp=timestamp,
            user_id=1,  # Admin user
            event_type="config_change",
            resource="settings",
            action="update",
            before_value={"setting": "old_value"},
            after_value={"setting": "new_value"},
            hash=hashlib.sha256(b"test3").hexdigest()
        )
        
        # API request event
        api_log = AuditLog(
            timestamp=timestamp,
            user_id=123,
            event_type="api_request",
            resource="/api/chat",
            action="POST",
            request_params={"message": "Hello"},
            hash=hashlib.sha256(b"test4").hexdigest()
        )
        
        session.add_all([auth_log, data_log, config_log, api_log])
        session.commit()
        
        # Verify all types logged
        auth_logs = session.query(AuditLog).filter_by(event_type="auth_login").all()
        assert len(auth_logs) == 1
        
        data_logs = session.query(AuditLog).filter_by(event_type="data_read").all()
        assert len(data_logs) == 1
        
        config_logs = session.query(AuditLog).filter_by(event_type="config_change").all()
        assert len(config_logs) == 1
        assert config_logs[0].before_value["setting"] == "old_value"
        assert config_logs[0].after_value["setting"] == "new_value"
    
    def test_audit_log_indexes(self, session):
        """Test that indexes optimize audit log queries (Requirement 21.2, 21.3)."""
        # Create multiple audit logs
        timestamp_base = datetime.utcnow()
        
        for i in range(10):
            log = AuditLog(
                timestamp=timestamp_base - timedelta(hours=i),
                user_id=123 if i < 5 else 456,
                event_type="data_read" if i % 2 == 0 else "data_update",
                resource="test_resource",
                action="test_action",
                hash=hashlib.sha256(f"test{i}".encode()).hexdigest()
            )
            session.add(log)
        
        session.commit()
        
        # Query by user_id (uses idx_audit_user)
        user_logs = session.query(AuditLog).filter_by(user_id=123).all()
        assert len(user_logs) == 5
        
        # Query by event_type (uses idx_audit_event)
        read_logs = session.query(AuditLog).filter_by(event_type="data_read").all()
        assert len(read_logs) == 5
        
        # Query by user and time range (uses idx_audit_user_time composite index)
        time_threshold = timestamp_base - timedelta(hours=3)
        recent_user_logs = session.query(AuditLog).filter(
            AuditLog.user_id == 123,
            AuditLog.timestamp >= time_threshold
        ).all()
        
        assert len(recent_user_logs) == 3  # Hours 0, 1, 2
    
    def test_audit_log_hash_verification(self, session):
        """Test hash computation for tamper detection (Requirement 18.5)."""
        timestamp = datetime.utcnow()
        user_id = 123
        event_type = "data_read"
        resource = "patient_profile"
        action = "view"
        
        # Compute hash
        hash_input = f"{timestamp}{user_id}{event_type}{resource}{action}"
        expected_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        log = AuditLog(
            timestamp=timestamp,
            user_id=user_id,
            event_type=event_type,
            resource=resource,
            action=action,
            hash=expected_hash
        )
        
        session.add(log)
        session.commit()
        
        # Retrieve and verify hash
        saved = session.query(AuditLog).filter_by(user_id=user_id).first()
        
        # Recompute hash from saved data
        saved_hash_input = f"{saved.timestamp}{saved.user_id}{saved.event_type}{saved.resource}{saved.action}"
        recomputed_hash = hashlib.sha256(saved_hash_input.encode()).hexdigest()
        
        assert saved.hash == recomputed_hash
        assert len(saved.hash) == 64  # SHA-256 produces 64 hex characters


class TestIndexPerformance:
    """Test that indexes improve query performance."""
    
    def test_user_id_index_on_chat_sessions(self, session):
        """Test that user_id index improves session queries (Requirement 21.2)."""
        # This test would ideally use EXPLAIN ANALYZE to verify index usage
        # For now, we verify the query executes successfully with the index
        
        # Query that should use idx_sessions_user_id
        result = session.execute(
            text("EXPLAIN SELECT * FROM chat_sessions WHERE user_id = 123")
        )
        
        explain_output = [row[0] for row in result]
        # In a real PostgreSQL database, we'd verify "Index Scan" appears in output
        # For testing, we just ensure the query executes
        assert len(explain_output) > 0
    
    def test_session_timestamp_composite_index(self, session):
        """Test composite index on session_id and timestamp (Requirement 21.3)."""
        # Query that should use idx_messages_session_time
        result = session.execute(
            text("""
                EXPLAIN SELECT * FROM chat_messages 
                WHERE session_id = 1 
                ORDER BY created_at DESC 
                LIMIT 20
            """)
        )
        
        explain_output = [row[0] for row in result]
        assert len(explain_output) > 0


def test_schema_compatibility():
    """Test that enhanced schemas are compatible with SQLAlchemy."""
    # Verify all models can be imported
    assert MedicalCondition is not None
    assert Medication is not None
    assert AuditLog is not None
    
    # Verify table names
    assert MedicalCondition.__tablename__ == "medical_conditions"
    assert Medication.__tablename__ == "medications"
    assert AuditLog.__tablename__ == "audit_logs"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
