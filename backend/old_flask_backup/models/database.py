"""
Database Connection Manager
============================
Production-grade PostgreSQL connection pooling and management.

This module provides a centralized, reusable database connection manager
that integrates with the application configuration system.

Design Decisions:
- Located in models/ (Data Access Layer) - handles all database interactions
- Uses singleton pattern for connection pool management
- Integrates with config.config for environment-based configuration
- Provides context managers for safe resource handling
- Implements connection pooling for performance and scalability

Usage:
    from models.database import get_db_connection
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
"""

import os
from contextlib import contextmanager
import psycopg
from psycopg_pool import ConnectionPool
from config.config import Config
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)


class DatabaseConnectionManager:
    """
    Singleton Database Connection Pool Manager.
    
    Manages PostgreSQL connections using a thread-safe connection pool
    for efficient resource utilization and optimal performance.
    
    Attributes:
        _instance: Singleton instance
        _connection_pool: psycopg2 ThreadedConnectionPool instance
    """
    
    _instance = None
    _connection_pool = None
    
    def __new__(cls):
        """
        Implement singleton pattern.
        
        Ensures only one connection pool exists for the entire application.
        """
        if cls._instance is None:
            cls._instance = super(DatabaseConnectionManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize connection pool if not already initialized."""
        if self._connection_pool is None:
            self._initialize_pool()
    
    def _initialize_pool(self):
        """
        Initialize PostgreSQL connection pool.
        
        Reads database configuration from Config class and creates
        a connection pool with configurable min/max connections.
        
        Raises:
            psycopg.Error: If connection pool creation fails
        """
        try:
            # Build database connection string for psycopg3
            conninfo = f"host={Config.DB_HOST} port={Config.DB_PORT} dbname={Config.DB_NAME} user={Config.DB_USER} password={Config.DB_PASSWORD}"
            
            # Create connection pool (psycopg3 syntax)
            self._connection_pool = ConnectionPool(
                conninfo=conninfo,
                min_size=Config.DB_POOL_MIN,
                max_size=Config.DB_POOL_MAX
            )
            
            logger.info("="*60)
            logger.info("Database Connection Pool Initialized")
            logger.info(f"  Host: {Config.DB_HOST}:{Config.DB_PORT}")
            logger.info(f"  Database: {Config.DB_NAME}")
            logger.info(f"  User: {Config.DB_USER}")
            logger.info(f"  Pool Size: {Config.DB_POOL_MIN} - {Config.DB_POOL_MAX} connections")
            logger.info("="*60)
            
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Context manager to safely acquire and release a database connection.
        
        Automatically returns the connection to the pool after use.
        Handles exceptions and ensures proper resource cleanup.
        
        Usage:
            db_manager = DatabaseConnectionManager()
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users")
                results = cursor.fetchall()
        
        Yields:
            psycopg.Connection: Database connection from the pool
            
        Raises:
            Exception: If connection acquisition fails
        """
        with self._connection_pool.connection() as connection:
            yield connection
    
    @contextmanager
    def get_cursor(self, commit=False):
        """
        Context manager to safely acquire a database cursor.
        
        Automatically handles connection management, commits, and rollbacks.
        This is a higher-level abstraction over get_connection().
        
        Args:
            commit (bool): Whether to commit the transaction on success
        
        Usage:
            db_manager = DatabaseConnectionManager()
            with db_manager.get_cursor(commit=True) as cursor:
                cursor.execute("INSERT INTO users (...) VALUES (...)")
        
        Yields:
            psycopg.Cursor: Database cursor
            
        Raises:
            psycopg.Error: If query execution fails
        """
        with self._connection_pool.connection() as connection:
            with connection.cursor() as cursor:
                try:
                    yield cursor
                    if commit:
                        connection.commit()
                except Exception as e:
                    logger.error(f"Database query error: {e}")
                    connection.rollback()
                    raise
    
    def test_connection(self):
        """
        Test database connectivity.
        
        Performs a simple query to verify database connection is working.
        Useful for health checks and startup validation.
        
        Returns:
            bool: True if connection test succeeds, False otherwise
        """
        try:
            with self.get_cursor() as cursor:
                # Execute simple test query
                cursor.execute("SELECT version();")
                db_version = cursor.fetchone()
                
                logger.info("[OK] Database connection test successful")
                logger.info(f"  PostgreSQL version: {db_version[0][:50]}...")
                
                return True
                
        except Exception as e:
            logger.error(f"✗ Database connection test failed: {e}")
            return False
    
    def close_all_connections(self):
        """
        Close all connections in the pool.
        
        Should be called during application shutdown for graceful cleanup.
        """
        if self._connection_pool:
            self._connection_pool.close()
            logger.info("All database connections closed")


# ============================================
# Convenience Functions
# ============================================

# Global singleton instance
_db_instance = None


def get_db_manager():
    """
    Get the global database connection manager instance.
    
    Returns:
        DatabaseConnectionManager: Singleton database manager
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseConnectionManager()
    return _db_instance


@contextmanager
def get_db_connection():
    """
    Convenience function to get a database connection.
    
    Usage:
        from models.database import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
    
    Yields:
        psycopg2.connection: Database connection
    """
    db_manager = get_db_manager()
    with db_manager.get_connection() as conn:
        yield conn


@contextmanager
def get_db_cursor(commit=False):
    """
    Convenience function to get a database cursor.
    
    Args:
        commit (bool): Whether to commit the transaction
    
    Usage:
        from models.database import get_db_cursor
        
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO users (...) VALUES (...)")
    
    Yields:
        psycopg2.cursor: Database cursor
    """
    db_manager = get_db_manager()
    with db_manager.get_cursor(commit=commit) as cursor:
        yield cursor


def test_database_connection():
    """
    Test database connectivity.
    
    Returns:
        bool: True if successful, False otherwise
    """
    db_manager = get_db_manager()
    return db_manager.test_connection()
