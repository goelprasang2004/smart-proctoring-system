"""
Insert admin user if doesn't exist
"""
import psycopg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'prasang-project')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD')

print("Checking admin user...")

try:
    # Connect to database
    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    with conn.cursor() as cur:
        # Check if admin user exists
        cur.execute("SELECT * FROM users WHERE email = 'admin@gmail.com'")
        admin = cur.fetchone()
        
        if admin:
            print("[OK] Admin user already exists")
            print(f"  Email: admin@gmail.com")
            print(f"  Role: {admin[3] if admin else 'N/A'}")
        else:
            print("[X] Admin user not found, creating...")
            
            # Insert admin user
            cur.execute("""
                INSERT INTO users (email, password_hash, role, full_name, is_active)
                VALUES (
                    'admin@gmail.com',
                    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIeWJ7GRJu',
                    'admin',
                    'System Administrator',
                    TRUE
                )
            """)
            conn.commit()
            print("[OK] Admin user created successfully")
        
        # Also check for student user
        cur.execute("SELECT * FROM users WHERE email = 'student@example.com'")
        student = cur.fetchone()
        
        if not student:
            print("Creating test student user...")
            cur.execute("""
                INSERT INTO users (email, password_hash, role, full_name)
                VALUES (
                    'student@example.com',
                    '$2b$12$KIXvZ3H5y8n3UQ0J8F0HNuN7LQ3xJ5yN8L0H2F3K4L5M6N7O8P9Q0',
                    'student',
                    'Test Student'
                )
            """)
            conn.commit()
            print("[OK] Test student user created")
        else:
            print("[OK] Test student user already exists")
    
    print("\n" + "=" * 60)
    print("Login Credentials:")
    print("=" * 60)
    print("Admin:")
    print("  Email: admin@gmail.com")
    print("  Password: StrongPassword123!")
    print()
    print("Student:")
    print("  Email: student@example.com")
    print("  Password: TestStudent123!")
    print("=" * 60)
    
    conn.close()
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()
