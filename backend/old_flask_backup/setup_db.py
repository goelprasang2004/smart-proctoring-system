"""
Quick database setup script
Executes MANUAL_SETUP.sql automatically
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

print("=" * 60)
print("Smart Proctoring System - Database Setup")
print("=" * 60)

try:
    # Connect to database
    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    print(f"[OK] Connected to database: {DB_NAME}")
    
    # Read SQL file
    with open('database/MANUAL_SETUP.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    
    print("[OK] Read MANUAL_SETUP.sql")
    
    # Execute SQL
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()
    
    print("[OK] Database schema created")
    print("[OK] Admin user created")
    print("[OK] Genesis block created")
    print("=" * 60)
    print("Setup completed successfully!")
    print("=" * 60)
    print("Default admin credentials:")
    print("  Email: admin@gmail.com")
    print("  Password: StrongPassword123!")
    print("=" * 60)
    
    conn.close()
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()
