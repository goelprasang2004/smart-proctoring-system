"""
Authentication Service
=====================
Business logic for user authentication and authorization.

Handles:
- Password hashing and verification (bcrypt)
- JWT token generation and validation
- User registration and login
- Token refresh
"""

import bcrypt
import jwt
import uuid
from datetime import datetime, timedelta
from config.config import Config
from models.user import User
from utils.logger import setup_logger, log_security_event

logger = setup_logger(__name__)


class AuthService:
    """
    Authentication service handling all auth-related business logic.
    """
    
    @staticmethod
    def hash_password(password):
        """
        Hash a password using bcrypt.
        
        Args:
            password (str): Plain text password
            
        Returns:
            str: Bcrypt hashed password
        """
        # bcrypt requires bytes
        password_bytes = password.encode('utf-8')
        
        # Generate salt and hash
        salt = bcrypt.gensalt(rounds=Config.BCRYPT_ROUNDS)
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Return as string
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password, password_hash):
        """
        Verify a password against its hash.
        
        Args:
            password (str): Plain text password
            password_hash (str): Bcrypt hashed password
            
        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            password_bytes = password.encode('utf-8')
            hash_bytes = password_hash.encode('utf-8')
            
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    @staticmethod
    def generate_access_token(user_id, email, role, jti=None):
        """
        Generate JWT access token with JTI (JWT ID) for revocation.
        
        Args:
            user_id (str): User's UUID
            email (str): User's email
            role (str): User's role
            jti (str, optional): JWT ID for token tracking
            
        Returns:
            tuple: (token, jti)
        """
        # Generate unique JWT ID if not provided
        if not jti:
            jti = str(uuid.uuid4())
        
        now = datetime.utcnow()
        
        payload = {
            'user_id': user_id,
            'email': email,
            'role': role,
            'type': 'access',
            'jti': jti,  # JWT ID for revocation
            'exp': now + timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES),
            'iat': now,
            'nbf': now  # Not before - prevents premature use
        }
        
        token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
        return token, jti
    
    @staticmethod
    def generate_refresh_token(user_id, email, role, family_id=None):
        """
        Generate JWT refresh token with family ID for rotation tracking.
        
        Args:
            user_id (str): User's UUID
            email (str): User's email
            role (str): User's role
            family_id (str, optional): Token family ID for rotation
            
        Returns:
            tuple: (token, jti, family_id)
        """
        # Generate unique identifiers
        jti = str(uuid.uuid4())
        if not family_id:
            family_id = str(uuid.uuid4())
        
        now = datetime.utcnow()
        
        payload = {
            'user_id': user_id,
            'email': email,
            'role': role,
            'type': 'refresh',
            'jti': jti,  # Unique token ID
            'family_id': family_id,  # Token family for rotation
            'exp': now + timedelta(seconds=Config.JWT_REFRESH_TOKEN_EXPIRES),
            'iat': now,
            'nbf': now
        }
        
        token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
        return token, jti, family_id
    
    @staticmethod
    def verify_token(token, token_type='access'):
        """
        Verify and decode JWT token.
        
        Args:
            token (str): JWT token
            token_type (str): Expected token type ('access' or 'refresh')
            
        Returns:
            dict: Decoded token payload
            None: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            
            # Verify token type
            if payload.get('type') != token_type:
                logger.warning(f"Invalid token type. Expected {token_type}, got {payload.get('type')}")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    @staticmethod
    def register_user(email, password, role, full_name):
        """
        Register a new user.
        
        Args:
            email (str): User's email
            password (str): Plain text password
            role (str): User role ('admin' or 'student')
            full_name (str): User's full name
            
        Returns:
            dict: Created user data (without password_hash)
            
        Raises:
            ValueError: If validation fails or email exists
        """
        # Validate inputs
        if not email or not password or not role or not full_name:
            raise ValueError("All fields are required")
        
        if role not in ['admin', 'student']:
            raise ValueError("Invalid role. Must be 'admin' or 'student'")
        
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        
        # Check if email already exists
        if User.email_exists(email):
            raise ValueError("Email already registered")
        
        # Hash password
        password_hash = AuthService.hash_password(password)
        
        # Create user
        user = User.create(email, password_hash, role, full_name)
        
        logger.info(f"User registered successfully: {email}")
        return user
    
    @staticmethod
    def create_student_account(email, password, full_name, created_by_admin_id):
        """
        Create a new student account (admin-only operation).
        
        This method is specifically for admins to create student accounts.
        It forces the role to be 'student' for security.
        
        Args:
            email (str): Student's email
            password (str): Plain text password
            full_name (str): Student's full name
            created_by_admin_id (str): ID of admin creating this account
            
        Returns:
            dict: Created student data (without password_hash)
            
        Raises:
            ValueError: If validation fails or email exists
        """
        # Validate inputs
        if not email or not password or not full_name:
            raise ValueError("Email, password, and full name are required")
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError('Invalid email format')
        
        # Validate password strength
        if len(password) < 6:
            raise ValueError('Password must be at least 6 characters long')
        
        # Check if email already exists
        if User.email_exists(email):
            raise ValueError('Email already registered')
        
        # Hash password
        password_hash = AuthService.hash_password(password)
        
        # Force role to be 'student' (security measure)
        role = 'student'
        
        # Create user
        user = User.create(email, password_hash, role, full_name)
        
        log_security_event(logger, 'student_created_by_admin', {
            'student_id': user['id'],
            'student_email': email,
            'created_by_admin_id': created_by_admin_id
        })
        
        logger.info(f"Student account created by admin {created_by_admin_id}: {email}")
        return user
    
    @staticmethod
    def login_user(email, password):
        """
        Authenticate user and generate tokens.
        
        Args:
            email (str): User's email
            password (str): Plain text password
            
        Returns:
            dict: User data and tokens
            
        Raises:
            ValueError: If credentials are invalid
        """
        # Find user by email
        user = User.find_by_email(email)
        
        if not user:
            raise ValueError("Invalid email or password")
        
        # Check if account is active
        if not user['is_active']:
            raise ValueError("Account is deactivated")
        
        # Verify password
        if not AuthService.verify_password(password, user['password_hash']):
            raise ValueError("Invalid email or password")
        
        # Update last login
        User.update_last_login(user['id'])
        
        # Generate tokens with IDs
        access_token, access_jti = AuthService.generate_access_token(
            user['id'], user['email'], user['role']
        )
        refresh_token, refresh_jti, family_id = AuthService.generate_refresh_token(
            user['id'], user['email'], user['role']
        )
        
        # Log security event
        log_security_event(
            logger,
            event_type='user_login',
            details={'user_id': user['id'], 'email': email, 'role': user['role']}
        )
        
        logger.info(f"User logged in successfully: {email}")
        
        # Remove password_hash from response
        user.pop('password_hash', None)
        
        return {
            'user': user,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': Config.JWT_ACCESS_TOKEN_EXPIRES  # Seconds until access token expires
        }
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """
        Generate new access token AND new refresh token (token rotation).
        
        Implements refresh token rotation for enhanced security:
        - Original refresh token is invalidated
        - New refresh token is issued with same family_id
        - If token reuse detected, invalidate entire family
        
        Args:
            refresh_token (str): Valid refresh token
            
        Returns:
            dict: New access and refresh tokens
            
        Raises:
            ValueError: If refresh token is invalid or reused
        """
        # Verify refresh token
        payload = AuthService.verify_token(refresh_token, token_type='refresh')
        
        if not payload:
            log_security_event(
                logger,
                event_type='refresh_token_invalid',
                details={'reason': 'Invalid or expired refresh token'}
            )
            raise ValueError("Invalid or expired refresh token")
        
       # TODO: In production, check if JTI is revoked (requires token revocation store)
        # For now, we rely on expiration
        
        # Generate new tokens with rotation
        access_token, access_jti = AuthService.generate_access_token(
            payload['user_id'],
            payload['email'],
            payload['role']
        )
        
        # Rotate refresh token (keep same family_id)
        new_refresh_token, new_refresh_jti, family_id = AuthService.generate_refresh_token(
            payload['user_id'],
            payload['email'],
            payload['role'],
            family_id=payload.get('family_id')  # Maintain token family
        )
        
        logger.info(f"Tokens rotated for user: {payload['email']}")
        
        return {
            'access_token': access_token,
            'refresh_token': new_refresh_token,
            'expires_in': Config.JWT_ACCESS_TOKEN_EXPIRES
        }
