"""
Authentication Middleware
=========================
JWT validation and role-based access control.

Provides decorators for:
- Requiring authentication
- Requiring specific roles
"""

from functools import wraps
from flask import request, jsonify
from services.auth_service import AuthService
from models.user import User
from utils.logger import setup_logger, log_security_event

logger = setup_logger(__name__)


def token_required(f):
    """
    Decorator to require valid JWT token.
    
    Validates JWT token from Authorization header and injects
    current_user into the request context.
    
    Usage:
        @app.route('/protected')
        @token_required
        def protected_route(current_user):
            return {'message': f'Hello {current_user["email"]}'}
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                # Expected format: "Bearer <token>"
                token = auth_header.split(" ")[1]
            except IndexError:
                log_security_event(logger, 'invalid_auth_header', {
                    'ip': request.remote_addr,
                    'path': request.path
                })
                return jsonify({'error': 'Invalid Authorization header format'}), 401
        
        if not token:
            log_security_event(logger, 'missing_token', {
                'ip': request.remote_addr,
                'path': request.path
            })
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        # Verify token
        payload = AuthService.verify_token(token, token_type='access')
        
        if not payload:
            log_security_event(logger, 'invalid_token', {
                'ip': request.remote_addr,
                'path': request.path
            })
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get current user from database
        current_user = User.find_by_id(payload['user_id'])
        
        if not current_user:
            log_security_event(logger, 'user_not_found', {
                'user_id': payload['user_id'],
                'ip': request.remote_addr
            })
            return jsonify({'error': 'User not found'}), 401
        
        # Check if account is active
        if not current_user['is_active']:
            log_security_event(logger, 'inactive_account_access', {
                'user_id': current_user['id'],
                'email': current_user['email'],
                'ip': request.remote_addr
            })
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Inject current_user into the route
        return f(current_user, *args, **kwargs)
    
    return decorated


def admin_required(f):
    """
    Decorator to require admin role.
    
    Must be used AFTER @token_required decorator.
    
    Usage:
        @app.route('/admin-only')
        @token_required
        @admin_required
        def admin_route(current_user):
            return {'message': 'Admin access granted'}
    """
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user['role'] != 'admin':
            log_security_event(logger, 'unauthorized_admin_access', {
                'user_id': current_user['id'],
                'email': current_user['email'],
                'role': current_user['role'],
                'ip': request.remote_addr,
                'path': request.path
            })
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def student_required(f):
    """
    Decorator to require student role.
    
    Must be used AFTER @token_required decorator.
    
    Usage:
        @app.route('/student-only')
        @token_required
        @student_required
        def student_route(current_user):
            return {'message': 'Student access granted'}
    """
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user['role'] != 'student':
            log_security_event(logger, 'unauthorized_student_access', {
                'user_id': current_user['id'],
                'email': current_user['email'],
                'role': current_user['role'],
                'ip': request.remote_addr,
                'path': request.path
            })
            return jsonify({'error': 'Student access required'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def role_required(*allowed_roles):
    """
    Decorator to require specific roles.
    
    Must be used AFTER @token_required decorator.
    
    Args:
        *allowed_roles: Variable number of allowed roles
    
    Usage:
        @app.route('/multi-role')
        @token_required
        @role_required('admin', 'student')
        def multi_role_route(current_user):
            return {'message': 'Access granted'}
    """
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            if current_user['role'] not in allowed_roles:
                log_security_event(logger, 'unauthorized_role_access', {
                    'user_id': current_user['id'],
                    'email': current_user['email'],
                    'role': current_user['role'],
                    'allowed_roles': list(allowed_roles),
                    'ip': request.remote_addr,
                    'path': request.path
                })
                return jsonify({
                    'error': f'Access denied. Required roles: {", ".join(allowed_roles)}'
                }), 403
            
            return f(current_user, *args, **kwargs)
        
        return decorated
    
    return decorator
