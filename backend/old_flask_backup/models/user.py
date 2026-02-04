"""
User Model
==========
Data access layer for user-related database operations.

This module provides all database queries for user management,
following the repository pattern.
"""

from models.database import get_db_cursor
from utils.logger import setup_logger
import uuid

logger = setup_logger(__name__)


class User:
    """
    User model representing admin and student accounts.
    
    Provides methods for user CRUD operations and authentication queries.
    """
    
    @staticmethod
    def create(email, password_hash, role, full_name):
        """
        Create a new user in the database.
        
        Args:
            email (str): User's email address (unique)
            password_hash (str): Bcrypt hashed password
            role (str): User role ('admin' or 'student')
            full_name (str): User's full name
            
        Returns:
            dict: Created user data (without password_hash)
            
        Raises:
            Exception: If user creation fails (e.g., duplicate email)
        """
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    INSERT INTO users (email, password_hash, role, full_name)
                    VALUES (%s, %s, %s::user_role, %s)
                    RETURNING id, email, role, full_name, created_at, is_active;
                """, (email, password_hash, role, full_name))
                
                user = cursor.fetchone()
                
                logger.info(f"User created: {email} (role: {role})")
                
                return {
                    'id': str(user[0]),
                    'email': user[1],
                    'role': user[2],
                    'full_name': user[3],
                    'created_at': user[4].isoformat() if user[4] else None,
                    'is_active': user[5]
                }
                
        except Exception as e:
            logger.error(f"Failed to create user {email}: {e}")
            raise
    
    @staticmethod
    def find_by_email(email):
        """
        Find user by email address.
        
        Args:
            email (str): User's email address
            
        Returns:
            dict: User data including password_hash (for authentication)
            None: If user not found
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT id, email, password_hash, role, full_name, 
                           created_at, updated_at, is_active, last_login
                    FROM users
                    WHERE email = %s;
                """, (email,))
                
                user = cursor.fetchone()
                
                if not user:
                    return None
                
                return {
                    'id': str(user[0]),
                    'email': user[1],
                    'password_hash': user[2],
                    'role': user[3],
                    'full_name': user[4],
                    'created_at': user[5].isoformat() if user[5] else None,
                    'updated_at': user[6].isoformat() if user[6] else None,
                    'is_active': user[7],
                    'last_login': user[8].isoformat() if user[8] else None
                }
                
        except Exception as e:
            logger.error(f"Failed to find user by email {email}: {e}")
            raise
    
    @staticmethod
    def find_by_id(user_id):
        """
        Find user by ID.
        
        Args:
            user_id (str): User's UUID
            
        Returns:
            dict: User data (without password_hash)
            None: If user not found
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT id, email, role, full_name, created_at, 
                           updated_at, is_active, last_login
                    FROM users
                    WHERE id = %s::uuid;
                """, (user_id,))
                
                user = cursor.fetchone()
                
                if not user:
                    return None
                
                return {
                    'id': str(user[0]),
                    'email': user[1],
                    'role': user[2],
                    'full_name': user[3],
                    'created_at': user[4].isoformat() if user[4] else None,
                    'updated_at': user[5].isoformat() if user[5] else None,
                    'is_active': user[6],
                    'last_login': user[7].isoformat() if user[7] else None
                }
                
        except Exception as e:
            logger.error(f"Failed to find user by ID {user_id}: {e}")
            raise
    
    @staticmethod
    def update_last_login(user_id):
        """
        Update user's last login timestamp.
        
        Args:
            user_id (str): User's UUID
            
        Returns:
            bool: True if update successful
        """
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    UPDATE users
                    SET last_login = CURRENT_TIMESTAMP
                    WHERE id = %s::uuid;
                """, (user_id,))
                
                logger.info(f"Updated last_login for user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update last_login for user {user_id}: {e}")
            raise
    
    @staticmethod
    def update_active_status(user_id, is_active):
        """
        Activate or deactivate a user account.
        
        Args:
            user_id (str): User's UUID
            is_active (bool): Active status
            
        Returns:
            bool: True if update successful
        """
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    UPDATE users
                    SET is_active = %s
                    WHERE id = %s::uuid;
                """, (is_active, user_id))
                
                action = "activated" if is_active else "deactivated"
                logger.info(f"User {user_id} {action}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update active status for user {user_id}: {e}")
            raise
    
    @staticmethod
    def email_exists(email):
        """
        Check if email already exists in database.
        
        Args:
            email (str): Email to check
            
        Returns:
            bool: True if email exists, False otherwise
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS(SELECT 1 FROM users WHERE email = %s);
                """, (email,))
                
                return cursor.fetchone()[0]
                
        except Exception as e:
            logger.error(f"Failed to check email existence: {e}")
            raise
    
    @staticmethod
    def get_all_users(role=None):
        """
        Get all users, optionally filtered by role.
        
        Args:
            role (str, optional): Filter by role ('admin' or 'student')
            
        Returns:
            list: List of user dictionaries (without password_hash)
        """
        try:
            with get_db_cursor() as cursor:
                if role:
                    cursor.execute("""
                        SELECT id, email, role, full_name, created_at, 
                               is_active, last_login
                        FROM users
                        WHERE role = %s::user_role
                        ORDER BY created_at DESC;
                    """, (role,))
                else:
                    cursor.execute("""
                        SELECT id, email, role, full_name, created_at, 
                               is_active, last_login
                        FROM users
                        ORDER BY created_at DESC;
                    """)
                
                users = cursor.fetchall()
                
                return [{
                    'id': str(user[0]),
                    'email': user[1],
                    'role': user[2],
                    'full_name': user[3],
                    'created_at': user[4].isoformat() if user[4] else None,
                    'is_active': user[5],
                    'last_login': user[6].isoformat() if user[6] else None
                } for user in users]
                
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            raise
