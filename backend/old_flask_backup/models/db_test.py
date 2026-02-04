"""
Database Connection Test Utility
=================================
Standalone script to verify database connectivity.

This script can be run independently to test database connection
before starting the full application.

Usage:
    python -m models.db_test
    
    or
    
    python models/db_test.py
"""

import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import get_db_manager, get_db_cursor
from config.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


def test_connection_basic():
    """Test basic database connectivity."""
    print("\n" + "="*70)
    print("DATABASE CONNECTION TEST")
    print("="*70)
    
    try:
        # Get database manager
        db_manager = get_db_manager()
        
        # Test connection
        if db_manager.test_connection():
            print("\n✅ SUCCESS: Database connection is working!")
            return True
        else:
            print("\n❌ FAILED: Database connection test failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_connection_detailed():
    """Perform detailed database connectivity test."""
    print("\n" + "-"*70)
    print("DETAILED CONNECTION TEST")
    print("-"*70)
    
    try:
        with get_db_cursor() as cursor:
            # Test 1: Get database version
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"\n✓ PostgreSQL Version:")
            print(f"  {version[:80]}")
            
            # Test 2: Check current database
            cursor.execute("SELECT current_database();")
            current_db = cursor.fetchone()[0]
            print(f"\n✓ Current Database: {current_db}")
            
            # Test 3: List all tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            print(f"\n✓ Available Tables ({len(tables)}):")
            if tables:
                for table in tables:
                    print(f"  • {table[0]}")
            else:
                print("  (No tables found - run schema.sql first)")
            
            # Test 4: Check connection pool status
            print(f"\n✓ Connection Pool Configuration:")
            print(f"  Min Connections: {Config.DB_POOL_MIN}")
            print(f"  Max Connections: {Config.DB_POOL_MAX}")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Detailed test failed: {e}")
        return False


def display_configuration():
    """Display current database configuration."""
    print("\n" + "-"*70)
    print("DATABASE CONFIGURATION")
    print("-"*70)
    
    # Mask password for security
    password_display = "***" if Config.DB_PASSWORD else "(not set)"
    
    print(f"\n  Host: {Config.DB_HOST}")
    print(f"  Port: {Config.DB_PORT}")
    print(f"  Database: {Config.DB_NAME}")
    print(f"  User: {Config.DB_USER}")
    print(f"  Password: {password_display}")
    print(f"  Pool Min: {Config.DB_POOL_MIN}")
    print(f"  Pool Max: {Config.DB_POOL_MAX}")


def main():
    """Main test execution."""
    # Display configuration
    display_configuration()
    
    # Run basic connection test
    basic_success = test_connection_basic()
    
    if basic_success:
        # Run detailed tests
        detailed_success = test_connection_detailed()
        
        print("\n" + "="*70)
        if detailed_success:
            print("✅ ALL TESTS PASSED")
        else:
            print("⚠️  BASIC CONNECTION OK, BUT DETAILED TESTS FAILED")
        print("="*70 + "\n")
        
        return detailed_success
    else:
        print("\n" + "="*70)
        print("❌ CONNECTION TEST FAILED")
        print("="*70)
        print("\nTroubleshooting:")
        print("  1. Verify PostgreSQL is running")
        print("  2. Check .env file has correct DB_PASSWORD")
        print("  3. Verify database 'proctoring_system' exists")
        print("  4. Check network connectivity to database host")
        print("="*70 + "\n")
        
        return False


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run tests
    success = main()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
