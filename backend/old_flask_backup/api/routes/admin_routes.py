"""
Admin Routes
============
API endpoints for admin-specific operations.

Endpoints:
- POST /api/admin/students - Create new student account (admin-only)
- GET /api/admin/students - Get all students (admin-only)
"""

from flask import Blueprint, request, jsonify
from middleware.auth_middleware import token_required, admin_required
from middleware.rate_limit import rate_limit, RateLimits
from models.user import User
from utils.logger import setup_logger
from utils.error_handlers import validate_required_fields, log_api_error
import bcrypt

logger = setup_logger(__name__)

# Create blueprint
admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/students', methods=['POST'])
@token_required
@admin_required
@rate_limit(**RateLimits.REGISTER)  # Same rate limit as registration
def create_student(current_user):
    """
    Create a new student account (admin-only).
    
    Admin can create student accounts with email and password.
    
    Request Body:
        {
            "email": "student@example.com",
            "password": "password123",
            "full_name": "Student Name"
        }
    
    Returns:
        201: Student created successfully
        400: Validation error or email already exists
        403: Not an admin
    """
    try:
        data = request.get_json()
        
        if not data:
            logger.warning(f"Create student with no data - Admin: {current_user['id']}")
            return jsonify({
                'error': 'Request body is required',
                'error_code': 'VAL_001'
            }), 400
        
        # Validate required fields
        required_fields = ['email', 'password', 'full_name']
        missing_fields = [f for f in required_fields if f not in data or not data[f]]
        
        if missing_fields:
            logger.warning(f"Create student missing fields: {missing_fields} - Admin: {current_user['id']}")
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}',
                'missing_fields': missing_fields,
                'error_code': 'VAL_008'
            }), 400
        
        logger.info(f"Creating student - Email: {data['email']}, Admin: {current_user['email']}")
        
        # Hash the password before storing
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user = User.create(
            email=data['email'],
            password_hash=password_hash,
            role='student',
            full_name=data['full_name']
        )
        
        logger.info(f"Student created successfully - Email: {data['email']}, ID: {user['id']}, by Admin: {current_user['email']}")
        
        return jsonify({
            'message': 'Student created successfully',
            'student': user
        }), 201
        
    except ValueError as e:
        logger.warning(f"Create student validation error - Admin: {current_user['id']}, Error: {str(e)}")
        return jsonify({
            'error': str(e),
            'error_code': 'ADMIN_001'
        }), 400
    except Exception as e:
        log_api_error('/admin/students', 'POST', e, current_user['id'], data)
        return jsonify({
            'error': 'Failed to create student',
            'error_code': 'ADMIN_002'
        }), 500


@admin_bp.route('/students', methods=['GET'])
@token_required
@admin_required
def get_all_students(current_user):
    """
    Get all student accounts (admin-only).
    
    Returns list of all students with their details.
    
    Returns:
        200: List of students
        403: Not an admin
        500: Server error
    """
    try:
        logger.info(f"Fetching all students - Admin: {current_user['email']}")
        
        students = User.get_all_users(role='student')
        
        logger.info(f"Retrieved {len(students)} students - Admin: {current_user['email']}")
        
        return jsonify({
            'students': students,
            'count': len(students)
        }), 200
        
    except Exception as e:
        log_api_error('/admin/students', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to get students',
            'error_code': 'ADMIN_003'
        }), 500
