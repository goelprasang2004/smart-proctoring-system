"""
Authentication Routes
====================
API endpoints for user authentication and authorization.

Endpoints:
- POST /api/auth/register - Register new user
- POST /api/auth/login - Login and get tokens
- POST /api/auth/refresh - Refresh access token
- GET /api/auth/me - Get current user info
- POST /api/auth/logout - Logout (client-side)
"""

from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from middleware.auth_middleware import token_required
from middleware.rate_limit import rate_limit, RateLimits
from models.user import User
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@rate_limit(**RateLimits.REGISTER)  # 3 requests per hour
def register():
    """
    Register a new user (admin or student).
    
    Request Body:
        {
            "email": "user@example.com",
            "password": "password123",
            "role": "admin" | "student",
            "full_name": "John Doe"
        }
    
    Returns:
        201: User created successfully
        400: Validation error or email already exists
    """
    try:
        data = request.get_json()
        
        if not data:
            logger.warning("Registration attempt with no JSON data")
            return jsonify({
                'error': 'Request body is required',
                'error_code': 'VAL_001'
            }), 400
        
        # Validate required fields
        required_fields = ['email', 'password', 'role', 'full_name']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            logger.warning(f"Registration attempt with missing fields: {missing_fields}")
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}',
                'missing_fields': missing_fields,
                'error_code': 'VAL_002'
            }), 400
        
        # Log sanitized registration attempt
        logger.info(f"Registration attempt for email: {data['email']}, role: {data['role']}")
        
        # Register user
        user = AuthService.register_user(
            email=data['email'],
            password=data['password'],
            role=data['role'],
            full_name=data['full_name']
        )
        
        logger.info(f"User registered successfully: {data['email']} (role: {data['role']})")
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user
        }), 201
        
    except ValueError as e:
        # Validation errors from service layer
        logger.warning(f"Registration validation error: {str(e)}")
        return jsonify({
            'error': str(e),
            'error_code': 'VAL_003'
        }), 400
    except Exception as e:
        # Unexpected errors
        logger.error(f"Registration error for email {data.get('email', 'unknown')}: {type(e).__name__}: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Registration failed due to an internal error',
            'error_code': 'REG_001'
        }), 500



@auth_bp.route('/login', methods=['POST'])
@rate_limit(**RateLimits.LOGIN)  # 5 requests per 5 minutes (anti-brute force)
def login():
    """
    Login and receive JWT tokens.
    
    Request Body:
        {
            "email": "user@example.com",
            "password": "password123"
        }
    
    Returns:
        200: Login successful with tokens
        400: Missing fields
        401: Invalid credentials
    """
    try:
        data = request.get_json()
        
        if not data:
            logger.warning(f"Login attempt with no JSON data from IP: {request.remote_addr}")
            return jsonify({
                'error': 'Request body is required',
                'error_code': 'VAL_001'
            }), 400
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            logger.warning(f"Login attempt with missing credentials from IP: {request.remote_addr}")
            return jsonify({
                'error': 'Email and password are required',
                'error_code': 'VAL_004'
            }), 400
        
        # Log login attempt (don't log the password!)
        logger.info(f"Login attempt for email: {data['email']} from IP: {request.remote_addr}")
        
        # Login user
        result = AuthService.login_user(
            email=data['email'],
            password=data['password']
        )
        
        logger.info(f"Successful login for user: {data['email']} (role: {result['user'].get('role', 'unknown')})")
        
        return jsonify({
            'message': 'Login successful',
            'user': result['user'],
            'access_token': result['access_token'],
            'refresh_token': result['refresh_token']
        }), 200
        
    except ValueError as e:
        # Invalid credentials
        email = data.get('email', 'unknown') if data else 'unknown'
        logger.warning(f"Failed login attempt for email: {email} from IP: {request.remote_addr} - {str(e)}")
        return jsonify({
            'error': str(e),
            'error_code': 'AUTH_001'
        }), 401
    except Exception as e:
        # Unexpected errors
        email = data.get('email', 'unknown') if data else 'unknown'
        logger.error(f"Login error for email {email}: {type(e).__name__}: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Login failed due to an internal error',
            'error_code': 'LOGIN_001'
        }), 500


@auth_bp.route('/refresh', methods=['POST'])
@rate_limit(**RateLimits.REFRESH)  # 10 requests per 5 minutes
def refresh():
    """
    Refresh access token using refresh token.
    
    Request Body:
        {
            "refresh_token": "eyJ..."
        }
    
    Returns:
        200: New access token
        400: Missing refresh token
        401: Invalid refresh token
    """
    try:
        data = request.get_json()
        
        if not data:
            logger.warning(f"Token refresh attempt with no JSON data from IP: {request.remote_addr}")
            return jsonify({
                'error': 'Request body is required',
                'error_code': 'VAL_001'
            }), 400
        
        if not data.get('refresh_token'):
            logger.warning(f"Token refresh attempt with no token from IP: {request.remote_addr}")
            return jsonify({
                'error': 'Refresh token is required',
                'error_code': 'VAL_005'
            }), 400
        
        # Refresh access token
        result = AuthService.refresh_access_token(data['refresh_token'])
        
        logger.info(f"Token refreshed successfully for user from IP: {request.remote_addr}")
        
        return jsonify({
            'message': 'Token refreshed successfully',
            'access_token': result['access_token']
        }), 200
        
    except ValueError as e:
        # Invalid token
        logger.warning(f"Token refresh failed from IP: {request.remote_addr} - {str(e)}")
        return jsonify({
            'error': str(e),
            'error_code': 'AUTH_002'
        }), 401
    except Exception as e:
        # Unexpected errors
        logger.error(f"Token refresh error: {type(e).__name__}: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Token refresh failed due to an internal error',
            'error_code': 'REFRESH_001'
        }), 500



@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """
    Get current authenticated user's information.
    
    Requires: Valid JWT access token in Authorization header
    
    Returns:
        200: User information
        401: Invalid or missing token
    """
    return jsonify({
        'user': current_user
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """
    Logout endpoint (client-side token removal).
    
    Note: Since we're using stateless JWT, actual logout is handled
    client-side by removing the tokens. This endpoint is provided
    for logging purposes.
    
    Requires: Valid JWT access token
    
    Returns:
        200: Logout successful
    """
    logger.info(f"User logged out: {current_user['email']}")
    
    return jsonify({
        'message': 'Logout successful'
    }), 200
