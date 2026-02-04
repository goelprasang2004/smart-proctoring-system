"""
Add missing columns to exam_attempts table
Run this script to fix the database schema
"""

from models.database import get_db_cursor
from utils.logger import setup_logger

logger = setup_logger(__name__)

def add_missing_columns():
    """Add missing columns to exam_attempts table"""
    try:
        with get_db_cursor(commit=True) as cursor:
            # Check if browser_metadata column exists
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'exam_attempts' AND column_name = 'browser_metadata'
            """)
            
            if not cursor.fetchone():
                print("Adding browser_metadata column...")
                cursor.execute("""
                    ALTER TABLE exam_attempts 
                    ADD COLUMN IF NOT EXISTS browser_metadata JSONB
                """)
                print("✓ browser_metadata column added")
            else:
                print("✓ browser_metadata column already exists")
            
            # Check if created_at column exists
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'exam_attempts' AND column_name = 'created_at'
            """)
            
            if not cursor.fetchone():
                print("Adding created_at column...")
                cursor.execute("""
                    ALTER TABLE exam_attempts 
                    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """)
                print("✓ created_at column added")
            else:
                print("✓ created_at column already exists")
                
            print("\n✅ Migration completed successfully!")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    add_missing_columns()
