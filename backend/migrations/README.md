# Database Migrations

## Overview

This directory contains database migrations for the AI Healthcare Chatbot enhancements.

## Migration 001: Enhanced PostgreSQL Schema

**Task**: 1.2 Enhance PostgreSQL database schema  
**Requirements**: 2.1, 16.4, 18.1, 21.2, 21.3

### What This Migration Adds

1. **medical_conditions table**
   - Stores 500+ medical conditions with symptoms, causes, and treatments
   - GIN index on symptoms array for fast full-text search
   - Tracks information freshness (last_updated, review_required)
   - Includes citation sources for HIPAA compliance

2. **medications table**
   - Stores medications with contraindications and drug interactions
   - Supports allergy checking and medication safety validation
   - Tracks drug-drug interactions

3. **audit_logs table**
   - Comprehensive HIPAA-compliant audit trail
   - Write-once constraint (immutable records)
   - SHA-256 hash for tamper detection
   - Tracks: authentication events, data access, config changes, API requests

4. **Optimized indexes**
   - Indexes on user_id, session_id, timestamp for existing tables
   - Composite indexes for common query patterns
   - GIN index for array-based full-text search

## Prerequisites

### PostgreSQL Setup

This migration requires PostgreSQL (version 12+). Install PostgreSQL:

**Windows:**
```bash
# Download from https://www.postgresql.org/download/windows/
# Or using Chocolatey:
choco install postgresql
```

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE healthcare;

# Create user (optional)
CREATE USER healthcare_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE healthcare TO healthcare_user;
```

### Update Configuration

Update `.env` file with PostgreSQL connection:

```env
DATABASE_URL=postgresql://healthcare_user:your_secure_password@localhost:5432/healthcare
```

Or for development (using postgres superuser):

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/healthcare
```

## Running the Migration

### Method 1: Python Script (Recommended)

```bash
# From backend directory
cd backend

# Run migration
python migrations/run_migration.py

# Or with custom database URL
python migrations/run_migration.py --database-url postgresql://user:pass@localhost:5432/healthcare
```

### Method 2: Direct SQL Execution

```bash
# Using psql
psql -U postgres -d healthcare -f migrations/001_enhance_schema.sql

# Or using connection string
psql postgresql://user:pass@localhost:5432/healthcare -f migrations/001_enhance_schema.sql
```

## Verification

After running the migration, verify the changes:

```sql
-- Check tables were created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('medical_conditions', 'medications', 'audit_logs');

-- Check indexes
SELECT tablename, indexname 
FROM pg_indexes 
WHERE tablename IN ('medical_conditions', 'medications', 'audit_logs')
ORDER BY tablename;

-- Check sample data
SELECT COUNT(*) FROM medical_conditions;
SELECT COUNT(*) FROM medications;

-- Verify GIN index on symptoms
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE indexname = 'idx_conditions_symptoms_gin';
```

## Rollback

To rollback the migration (⚠️ destroys data):

```bash
# Using Python script
python migrations/run_migration.py --rollback

# Or using SQL
psql -U postgres -d healthcare <<EOF
DROP TRIGGER IF EXISTS trg_prevent_audit_update ON audit_logs;
DROP TRIGGER IF EXISTS trg_prevent_audit_delete ON audit_logs;
DROP FUNCTION IF EXISTS prevent_audit_log_modification();
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS medications CASCADE;
DROP TABLE IF EXISTS medical_conditions CASCADE;
EOF
```

## Security Considerations

### Audit Log Write-Once Constraint

The audit_logs table has database-level triggers that prevent UPDATE and DELETE operations. For additional security in production:

```sql
-- Create restricted database user for application
CREATE USER app_user WITH PASSWORD 'secure_password';

-- Grant only INSERT on audit_logs
GRANT INSERT ON audit_logs TO app_user;
REVOKE UPDATE, DELETE ON audit_logs FROM app_user;

-- Grant full access to other tables
GRANT ALL ON medical_conditions, medications TO app_user;
GRANT ALL ON chat_messages, chat_sessions, users, patient_profiles TO app_user;
```

### Encryption

For production deployments with sensitive data:

1. Enable PostgreSQL SSL/TLS connections
2. Use encrypted storage for the database
3. Implement application-level encryption for PHI fields (see EncryptionService)

## Populating Data

### Medical Conditions

The migration includes 5 sample conditions. To populate with a full dataset (500+ conditions):

1. Obtain medical knowledge database (ICD-10, medical reference)
2. Create import script to parse and insert data
3. Ensure proper citation sources for all entries

```python
# Example: Import from CSV
import csv
from backend.app.database.connection import SessionLocal
from backend.app.models.enhanced_schemas import MedicalCondition

db = SessionLocal()

with open('medical_conditions.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        condition = MedicalCondition(
            name=row['name'],
            icd10_code=row['icd10_code'],
            symptoms=row['symptoms'].split('|'),
            causes=row['causes'],
            treatments=row['treatments'],
            severity=row['severity'],
            sources=row['sources'].split('|')
        )
        db.add(condition)
    
    db.commit()
```

### Medications

Similar process for medications database.

## Testing

After migration, test the schema:

```python
# Test medical conditions query
from backend.app.database.connection import SessionLocal
from backend.app.models.enhanced_schemas import MedicalCondition
from sqlalchemy import select

db = SessionLocal()

# Full-text search on symptoms (using GIN index)
result = db.execute(
    select(MedicalCondition)
    .where(MedicalCondition.symptoms.contains(['fever', 'cough']))
).scalars().all()

print(f"Found {len(result)} conditions with fever and cough")
```

## Performance Notes

- **GIN Index**: The GIN index on `medical_conditions.symptoms` enables fast full-text search across symptom arrays. This is optimized for read-heavy workloads.
  
- **Composite Indexes**: Indexes like `idx_audit_user_time` speed up common queries filtering by user and time range.

- **Index Maintenance**: PostgreSQL automatically maintains indexes. For large datasets, consider periodic `VACUUM` and `ANALYZE`.

## Troubleshooting

### Error: "relation already exists"

If you see this error, the migration may have already run. Check existing tables:

```sql
\dt
```

To force re-run, first rollback the migration.

### Error: "extension uuid-ossp does not exist"

Install the extension:

```sql
CREATE EXTENSION "uuid-ossp";
```

### Performance Issues

For large medical knowledge bases (10,000+ conditions), consider:

1. Increase PostgreSQL shared_buffers
2. Enable query result caching
3. Use connection pooling (PgBouncer)

## Next Steps

After migration:

1. ✅ Schema enhancement complete
2. ⬜ Implement KnowledgeBase service class
3. ⬜ Implement AuditLogger service class
4. ⬜ Populate medical_conditions with full dataset
5. ⬜ Implement contraindication checking
6. ⬜ Set up Redis cache for query optimization
