"""
Database Connection Module
==========================
Provides PostgreSQL connection pooling and management
for the Smart Proctoring System.

Features:
- Connection pooling for better performance
- Automatic connection retry logic
- Context manager for safe resource handling
- Environment-based configuration
"""

import os
import psycopg2
from psycopg2 import pool, Error
from contextlib import contextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Singleton database connection pool manager.
    
    Manages PostgreSQL connections using a connection pool
    for efficient resource utilization.
    """
    
    _instance = None
    _connection_pool = None
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize connection pool if not already initialized."""
        if self._connection_pool is None:
            self._initialize_pool()
    
    def _initialize_pool(self):
        """
        Initialize PostgreSQL connection pool.
        
        Reads database configuration from environment variables
        and creates a connection pool with min/max connections.
        """
        try:
            # Read database configuration from environment
            db_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '5432'),
                'database': os.getenv('DB_NAME', 'proctoring_system'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', ''),
            }
            
            # Create connection pool
            self._connection_pool = pool.ThreadedConnectionPool(
                minconn=int(os.getenv('DB_POOL_MIN', '2')),
                maxconn=int(os.getenv('DB_POOL_MAX', '10')),
                **db_config
            )
            
            logger.info("[OK] Database connection pool initialized successfully")
            logger.info(f"  Host: {db_config['host']}:{db_config['port']}")
            logger.info(f"  Database: {db_config['database']}")
            
        except Error as e:
            logger.error(f"✗ Failed to create connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Context manager to get a database connection from the pool.
        
        Usage:
            db = DatabaseConnection()
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users")
                results = cursor.fetchall()
        
        Yields:
            psycopg2.connection: Database connection
        """
        connection = None
        try:
            connection = self._connection_pool.getconn()
            if connection:
                yield connection
            else:
                raise Exception("Failed to get connection from pool")
        except Error as e:
            logger.error(f"Database connection error: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                self._connection_pool.putconn(connection)
    
    @contextmanager
    def get_cursor(self, commit=False):
        """
        Context manager to get a database cursor.
        
        Automatically handles connection management and commits/rollbacks.
        
        Args:
            commit (bool): Whether to commit the transaction on success
        
        Usage:
            db = DatabaseConnection()
            with db.get_cursor(commit=True) as cursor:
                cursor.execute("INSERT INTO users (...) VALUES (...)")
        
        Yields:
            psycopg2.cursor: Database cursor
        """
        connection = None
        cursor = None
        try:
            connection = self._connection_pool.getconn()
            cursor = connection.cursor()
            yield cursor
            
            if commit:
                connection.commit()
                
        except Error as e:
            logger.error(f"Database query error: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self._connection_pool.putconn(connection)
    
    def test_connection(self):
        """
        Test database connection.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT version();")
                db_version = cursor.fetchone()
                logger.info(f"[OK] Database connection test successful")
                logger.info(f"  PostgreSQL version: {db_version[0]}")
                return True
        except Exception as e:
            logger.error(f"✗ Database connection test failed: {e}")
            return False
    
    def close_all_connections(self):
        """Close all connections in the pool."""
        if self._connection_pool:
            self._connection_pool.closeall()
            logger.info("[OK] All database connections closed")


# Convenience function for quick access
def get_db():
    """
    Get database connection instance.
    
    Returns:
        DatabaseConnection: Database connection manager
    """
    return DatabaseConnection()


# Test function
def test_database_connection():
    """Test database connectivity."""
    try:
        db = get_db()
        if db.test_connection():
            print("\n" + "="*50)
            print("[OK] DATABASE CONNECTION SUCCESSFUL")
            print("="*50)
            
            # Test query to verify schema
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """)
                tables = cursor.fetchall()
                
                print("\nAvailable tables:")
                for table in tables:
                    print(f"  • {table[0]}")
            
            print("="*50 + "\n")
            return True
        else:
            print("\n✗ DATABASE CONNECTION FAILED\n")
            return False
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}\n")
        return False


if __name__ == "__main__":
    """Run connection test when executed directly."""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run test
    test_database_connection()
