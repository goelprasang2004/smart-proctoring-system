"""Clear the stuck exam attempt"""
from models.database import get_db_cursor

def clear_attempt():
    try:
        with get_db_cursor(commit=True) as cursor:
            # Delete all in_progress attempts
            cursor.execute("""
                DELETE FROM exam_attempts 
                WHERE status = 'in_progress'
            """)
            print("✅ All in-progress attempts cleared!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    clear_attempt()
