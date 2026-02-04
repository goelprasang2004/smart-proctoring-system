"""
Database Cleanup Utility
========================
Clears stuck exam attempts to allow new ones.
Run this when attempts are stuck in 'in_progress' state.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from models.database import get_db_cursor

def cleanup_stuck_attempts():
    """Clear all in-progress attempts (for testing only)"""
    try:
        with get_db_cursor() as cursor:
            # Just update status to completed
            cursor.execute("""
                UPDATE exam_attempts 
                SET status = 'completed'
                WHERE status = 'in_progress'
            """)
            
            affected = cursor.rowcount
            
            print(f"✅ Cleared {affected} stuck attempt(s)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    cleanup_stuck_attempts()
