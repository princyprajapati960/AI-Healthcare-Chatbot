-- Migration: Enhanced PostgreSQL Database Schema
-- Task: 1.2 Enhance PostgreSQL database schema
-- Requirements: 2.1, 16.4, 18.1, 21.2, 21.3
-- 
-- This migration creates:
-- - medical_conditions table with GIN index on symptoms array
-- - medications table with contraindications and interactions
-- - audit_logs table with write-once constraint
-- - indexes on frequently queried columns

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Medical Conditions Table
-- ============================================================================
-- Purpose: Store comprehensive medical knowledge base with 500+ conditions
-- Requirement 2.1: Enhanced Medical Knowledge Base

CREATE TABLE IF NOT EXISTS medical_conditions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    icd10_code VARCHAR(10),
    symptoms TEXT[] NOT NULL,
    causes TEXT,
    treatments TEXT,
    severity VARCHAR(50),
    sources TEXT[],
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    review_required BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- GIN index for fast full-text search on symptoms array (Requirement 21.2)
CREATE INDEX idx_conditions_symptoms_gin ON medical_conditions USING GIN(symptoms);

-- Additional indexes for optimization
CREATE INDEX idx_conditions_name ON medical_conditions(name);
CREATE INDEX idx_conditions_icd10 ON medical_conditions(icd10_code);
CREATE INDEX idx_conditions_updated ON medical_conditions(last_updated);

-- Add comment for documentation
COMMENT ON TABLE medical_conditions IS 'Medical conditions knowledge base for chatbot responses';
COMMENT ON COLUMN medical_conditions.symptoms IS 'Array of symptoms for GIN-indexed search';
COMMENT ON COLUMN medical_conditions.review_required IS 'Flag set when information exceeds 12 months age';

-- ============================================================================
-- Medications Table
-- ============================================================================
-- Purpose: Store medications with contraindications for safety checking
-- Requirement 3.2: Contraindication checking against user allergies

CREATE TABLE IF NOT EXISTS medications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    generic_name VARCHAR(255),
    contraindications TEXT[],
    side_effects TEXT[],
    interactions UUID[],
    dosage_forms TEXT[],
    pregnancy_category VARCHAR(10),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for medication lookups
CREATE INDEX idx_medications_name ON medications(name);
CREATE INDEX idx_medications_generic ON medications(generic_name);

-- Add comments
COMMENT ON TABLE medications IS 'Medications database with contraindications and drug interactions';
COMMENT ON COLUMN medications.contraindications IS 'Array of conditions/allergies that contraindicate this medication';
COMMENT ON COLUMN medications.interactions IS 'Array of medication UUIDs that interact with this drug';

-- ============================================================================
-- Audit Logs Table
-- ============================================================================
-- Purpose: Comprehensive HIPAA-compliant audit logging
-- Requirements: 16.4, 18.1, 18.2, 18.3, 18.4

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id INTEGER,
    event_type VARCHAR(50) NOT NULL,
    resource VARCHAR(255),
    action VARCHAR(50),
    ip_address INET,
    user_agent TEXT,
    request_params JSONB,
    before_value JSONB,
    after_value JSONB,
    hash CHAR(64) NOT NULL
);

-- Indexes for audit log queries (Requirement 21.2, 21.3)
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_event ON audit_logs(event_type);
CREATE INDEX idx_audit_resource ON audit_logs(resource);
CREATE INDEX idx_audit_user_time ON audit_logs(user_id, timestamp DESC);

-- Add comments
COMMENT ON TABLE audit_logs IS 'HIPAA-compliant audit trail with write-once constraint';
COMMENT ON COLUMN audit_logs.hash IS 'SHA-256 hash for tamper detection';
COMMENT ON COLUMN audit_logs.event_type IS 'Event types: auth_login, auth_logout, auth_failed, data_read, data_create, data_update, data_delete, config_change, api_request';

-- ============================================================================
-- Enhanced Indexes on Existing Tables
-- ============================================================================
-- Purpose: Optimize frequently queried columns for performance
-- Requirements: 21.2, 21.3

-- Indexes for chat_messages table
CREATE INDEX IF NOT EXISTS idx_messages_session_time ON chat_messages(session_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON chat_messages(created_at DESC);

-- Indexes for chat_sessions table
CREATE INDEX IF NOT EXISTS idx_sessions_user_active ON chat_sessions(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_sessions_user_started ON chat_sessions(user_id, started_at DESC);

-- Composite index for efficient session lookups
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON chat_sessions(user_id);

-- ============================================================================
-- Database Security Settings for Audit Logs (Write-Once Constraint)
-- ============================================================================
-- Note: These commands should be run with appropriate database admin privileges
-- Requirement 16.4: Immutable audit records

-- Create a trigger to prevent updates and deletes on audit_logs
-- This enforces the write-once constraint at the database level

CREATE OR REPLACE FUNCTION prevent_audit_log_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit logs cannot be modified or deleted';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_audit_update
    BEFORE UPDATE ON audit_logs
    FOR EACH ROW
    EXECUTE FUNCTION prevent_audit_log_modification();

CREATE TRIGGER trg_prevent_audit_delete
    BEFORE DELETE ON audit_logs
    FOR EACH ROW
    EXECUTE FUNCTION prevent_audit_log_modification();

-- ============================================================================
-- Sample Data Insertion (Optional - for development/testing)
-- ============================================================================

-- Insert sample medical conditions
INSERT INTO medical_conditions (name, icd10_code, symptoms, causes, treatments, severity, sources)
VALUES 
    (
        'Common Cold',
        'J00',
        ARRAY['runny nose', 'sore throat', 'cough', 'congestion', 'sneezing', 'mild headache'],
        'Viral infection, most commonly rhinovirus',
        'Rest, hydration, over-the-counter pain relievers, throat lozenges',
        'mild',
        ARRAY['CDC', 'Mayo Clinic']
    ),
    (
        'Influenza (Flu)',
        'J10',
        ARRAY['high fever', 'severe body aches', 'fatigue', 'cough', 'headache', 'chills'],
        'Influenza virus infection',
        'Antiviral medications (if within 48 hours), rest, hydration, fever reducers',
        'moderate',
        ARRAY['CDC', 'WHO']
    ),
    (
        'Migraine',
        'G43',
        ARRAY['severe headache', 'nausea', 'sensitivity to light', 'visual disturbances', 'throbbing pain'],
        'Neurological condition, triggers include stress, certain foods, hormonal changes',
        'Prescription migraine medications, rest in dark room, hydration',
        'moderate',
        ARRAY['American Migraine Foundation', 'NIH']
    ),
    (
        'Acute Bronchitis',
        'J20',
        ARRAY['persistent cough', 'chest discomfort', 'mucus production', 'fatigue', 'mild fever'],
        'Viral infection of bronchial tubes',
        'Rest, fluids, cough suppressants, humidifier use',
        'moderate',
        ARRAY['American Lung Association', 'Mayo Clinic']
    ),
    (
        'Gastroenteritis',
        'A09',
        ARRAY['diarrhea', 'nausea', 'vomiting', 'abdominal cramps', 'fever', 'dehydration'],
        'Viral or bacterial infection of digestive tract',
        'Oral rehydration, bland diet, rest, anti-diarrheal medications',
        'moderate',
        ARRAY['CDC', 'Cleveland Clinic']
    )
ON CONFLICT DO NOTHING;

-- Insert sample medications
INSERT INTO medications (name, generic_name, contraindications, side_effects, dosage_forms)
VALUES
    (
        'Aspirin',
        'acetylsalicylic acid',
        ARRAY['bleeding disorders', 'aspirin allergy', 'children with viral infections'],
        ARRAY['stomach upset', 'bleeding', 'allergic reactions'],
        ARRAY['tablet', 'chewable tablet', 'suppository']
    ),
    (
        'Ibuprofen',
        'ibuprofen',
        ARRAY['NSAID allergy', 'severe kidney disease', 'active bleeding', 'third trimester pregnancy'],
        ARRAY['stomach upset', 'nausea', 'dizziness', 'headache'],
        ARRAY['tablet', 'capsule', 'liquid suspension']
    ),
    (
        'Acetaminophen',
        'paracetamol',
        ARRAY['severe liver disease', 'acetaminophen allergy'],
        ARRAY['rare allergic reactions', 'liver damage at high doses'],
        ARRAY['tablet', 'capsule', 'liquid', 'suppository']
    ),
    (
        'Amoxicillin',
        'amoxicillin',
        ARRAY['penicillin allergy', 'severe kidney impairment'],
        ARRAY['diarrhea', 'nausea', 'rash', 'allergic reactions'],
        ARRAY['capsule', 'tablet', 'oral suspension']
    )
ON CONFLICT DO NOTHING;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Verify table creation
SELECT 
    'medical_conditions' as table_name, 
    COUNT(*) as row_count 
FROM medical_conditions
UNION ALL
SELECT 
    'medications' as table_name, 
    COUNT(*) as row_count 
FROM medications
UNION ALL
SELECT 
    'audit_logs' as table_name, 
    COUNT(*) as row_count 
FROM audit_logs;

-- Verify indexes were created
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename IN ('medical_conditions', 'medications', 'audit_logs', 'chat_messages', 'chat_sessions')
ORDER BY tablename, indexname;
