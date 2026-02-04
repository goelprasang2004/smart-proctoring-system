"""
Run Exam Assignments Migration
===============================
Execute the exam_assignments table migration.
"""

import os
import sys
from dotenv import load_dotenv
import psycopg

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Load environment variables
load_dotenv()

def run_migration():
    """Run the exam_assignments table migration."""
    print("=" * 60)
    print("Running Exam Assignments Migration")
    print("=" * 60)
    print()
    
    try:
        # Get database connection info from environment
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'dbname': os.getenv('DB_NAME', 'proctoring_system'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
        }
        
        print(f"Connecting to database: {db_config['dbname']}")
        
        # Connect to database
        conn = psycopg.connect(**db_config)
        cursor = conn.cursor()
        
        # Read migration SQL
        migration_path = os.path.join(
            os.path.dirname(__file__),
            'add_exam_assignments.sql'
        )
        
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        print("Executing migration SQL...")
        cursor.execute(migration_sql)
        conn.commit()
        print("✓ Migration executed successfully")
        print()
        
        # Verify table creation
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'exam_assignments'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        
        if columns:
            print("✓ exam_assignments table created with columns:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
        else:
            print("✗ Table not found after migration")
            cursor.close()
            conn.close()
            return False
        
        # Close connection
        cursor.close()
        conn.close()
        
        print()
        print("=" * 60)
        print("Migration Completed Successfully!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
