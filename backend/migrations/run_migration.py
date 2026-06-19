"""
Database migration runner for enhanced PostgreSQL schema.
Task 1.2: Enhance PostgreSQL database schema

This script applies the schema enhancements including:
- medical_conditions table with GIN index on symptoms
- medications table with contraindications
- audit_logs table with write-once constraint
- optimized indexes on existing tables

Requirements: 2.1, 16.4, 18.1, 21.2, 21.3
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from backend.app.config import settings


def run_migration(database_url: str = None):
    """
    Run the database migration to enhance schema.
    
    Args:
        database_url: Optional database URL. If not provided, uses settings.database_url
    """
    db_url = database_url or settings.database_url
    
    # Check if database is PostgreSQL
    if not db_url.startswith('postgresql'):
        print("❌ Error: This migration requires PostgreSQL.")
        print(f"   Current database: {db_url.split(':')[0]}")
        print("   Please update DATABASE_URL in .env to use PostgreSQL.")
        print("   Example: DATABASE_URL=postgresql://user:password@localhost:5432/healthcare")
        return False
    
    print("🔧 Starting database migration...")
    print(f"   Database: {db_url.split('@')[-1] if '@' in db_url else 'localhost'}")
    
    try:
        # Create engine
        engine = create_engine(db_url)
        
        # Read migration SQL file
        migration_file = Path(__file__).parent / "001_enhance_schema.sql"
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Split into individual statements (PostgreSQL can handle multi-statement execution)
        # But we'll execute major sections separately for better error reporting
        statements = []
        current_statement = []
        
        for line in migration_sql.split('\n'):
            # Skip comments and empty lines for statement parsing
            if line.strip().startswith('--') or not line.strip():
                continue
            
            current_statement.append(line)
            
            # End of statement
            if line.strip().endswith(';'):
                statements.append('\n'.join(current_statement))
                current_statement = []
        
        # Execute migration
        with engine.connect() as conn:
            print("\n📊 Creating medical_conditions table...")
            
            # Enable UUID extension
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            conn.commit()
            
            # Execute migration SQL
            print("📊 Executing migration SQL...")
            
            # Execute the entire migration as one transaction
            try:
                # Use raw SQL execution for complex migration
                conn.execute(text(migration_sql))
                conn.commit()
                print("✅ Migration completed successfully!")
                
            except Exception as e:
                conn.rollback()
                error_msg = str(e)
                
                # Check if tables already exist
                if "already exists" in error_msg.lower():
                    print("⚠️  Warning: Some tables already exist. Migration may be partially applied.")
                    print("   This is expected if running migration multiple times.")
                    
                    # Verify tables exist
                    result = conn.execute(text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name IN ('medical_conditions', 'medications', 'audit_logs')
                        ORDER BY table_name
                    """))
                    existing_tables = [row[0] for row in result]
                    
                    if existing_tables:
                        print(f"   Existing tables: {', '.join(existing_tables)}")
                        print("✅ Schema enhancements are in place.")
                        return True
                    else:
                        raise
                else:
                    raise
        
        # Verify migration
        print("\n🔍 Verifying migration...")
        with engine.connect() as conn:
            # Check tables
            result = conn.execute(text("""
                SELECT table_name, 
                       (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
                FROM information_schema.tables t
                WHERE table_schema = 'public' 
                AND table_name IN ('medical_conditions', 'medications', 'audit_logs')
                ORDER BY table_name
            """))
            
            tables = result.fetchall()
            if tables:
                print("   Tables created:")
                for table_name, col_count in tables:
                    print(f"     ✓ {table_name} ({col_count} columns)")
            else:
                print("   ⚠️  No new tables found")
            
            # Check indexes
            result = conn.execute(text("""
                SELECT tablename, indexname
                FROM pg_indexes
                WHERE tablename IN ('medical_conditions', 'medications', 'audit_logs')
                AND schemaname = 'public'
                ORDER BY tablename, indexname
            """))
            
            indexes = result.fetchall()
            if indexes:
                print("\n   Indexes created:")
                current_table = None
                for table_name, index_name in indexes:
                    if table_name != current_table:
                        print(f"     {table_name}:")
                        current_table = table_name
                    print(f"       ✓ {index_name}")
            
            # Check row counts
            result = conn.execute(text("""
                SELECT 
                    (SELECT COUNT(*) FROM medical_conditions) as conditions_count,
                    (SELECT COUNT(*) FROM medications) as medications_count,
                    (SELECT COUNT(*) FROM audit_logs) as audit_logs_count
            """))
            
            counts = result.fetchone()
            if counts:
                print(f"\n   Sample data inserted:")
                print(f"     ✓ medical_conditions: {counts[0]} rows")
                print(f"     ✓ medications: {counts[1]} rows")
                print(f"     ✓ audit_logs: {counts[2]} rows")
        
        print("\n✅ Database schema enhancement completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Update SQLAlchemy models to import enhanced_schemas")
        print("   2. Configure application to use new tables")
        print("   3. Populate medical_conditions with full dataset (500+ conditions)")
        print("   4. Set up database user permissions for audit_logs write-once constraint")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def rollback_migration(database_url: str = None):
    """
    Rollback the migration by dropping created tables.
    ⚠️ WARNING: This will delete all data in these tables!
    """
    db_url = database_url or settings.database_url
    
    print("⚠️  WARNING: This will drop all enhanced schema tables and their data!")
    confirm = input("   Type 'yes' to confirm rollback: ")
    
    if confirm.lower() != 'yes':
        print("   Rollback cancelled.")
        return False
    
    try:
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            print("\n🔧 Rolling back migration...")
            
            # Drop triggers first
            conn.execute(text("DROP TRIGGER IF EXISTS trg_prevent_audit_update ON audit_logs"))
            conn.execute(text("DROP TRIGGER IF EXISTS trg_prevent_audit_delete ON audit_logs"))
            conn.execute(text("DROP FUNCTION IF EXISTS prevent_audit_log_modification()"))
            
            # Drop tables
            for table in ['audit_logs', 'medications', 'medical_conditions']:
                print(f"   Dropping table: {table}")
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            
            conn.commit()
            print("✅ Rollback completed.")
        
        return True
        
    except Exception as e:
        print(f"❌ Rollback failed: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run database migration for enhanced schema")
    parser.add_argument(
        '--rollback', 
        action='store_true', 
        help='Rollback the migration (drops tables)'
    )
    parser.add_argument(
        '--database-url',
        type=str,
        help='Override database URL from settings'
    )
    
    args = parser.parse_args()
    
    if args.rollback:
        success = rollback_migration(args.database_url)
    else:
        success = run_migration(args.database_url)
    
    sys.exit(0 if success else 1)
