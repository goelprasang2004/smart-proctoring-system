"""
Exam Routes
===========
API endpoints for exam management.

Admin Endpoints:
- POST /api/exams - Create exam
- GET /api/exams - List all exams
- GET /api/exams/:id - Get exam details (with config)
- PUT /api/exams/:id - Update exam
- DELETE /api/exams/:id - Delete exam
- PATCH /api/exams/:id/status - Change exam status

Student Endpoints:
- GET /api/exams/available - List available exams
- GET /api/exams/:id/details - Get exam details (without config)
"""

from flask import Blueprint, request, jsonify
from services.exam_service import ExamService
from middleware.auth_middleware import token_required, admin_required, student_required
from utils.logger import setup_logger
from utils.error_handlers import log_api_error
import json

logger = setup_logger(__name__)

# Create blueprint
exams_bp = Blueprint('exams', __name__)


# ============================================
# ADMIN ENDPOINTS
# ============================================

@exams_bp.route('', methods=['POST'])
@token_required
@admin_required
def create_exam(current_user):
    """
    Create a new exam (Admin only).
    
    Request Body:
        {
            "title": "Final Exam",
            "description": "Final semester exam",
            "start_time": "2026-01-20T10:00:00",
            "end_time": "2026-01-20T12:00:00",
            "duration_minutes": 120,
            "exam_config": {
                "questions": [...],
                "settings": {...}
            }
        }
    
    Returns:
        201: Exam created successfully
        400: Validation error
    """
    try:
        data = request.get_json()
        
        if not data:
            logger.warning(f"Create exam with no data - Admin: {current_user['id']}")
            return jsonify({
                'error': 'Request body is required',
                'error_code': 'VAL_001'
            }), 400
        
        # Validate required fields
        required_fields = ['title', 'start_time', 'end_time', 'duration_minutes', 'exam_config']
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            logger.warning(f"Create exam missing fields: {missing_fields} - Admin: {current_user['id']}")
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}',
                'missing_fields': missing_fields,
                'error_code': 'VAL_008'
            }), 400
        
        logger.info(f"Creating exam - Title: {data['title']}, Admin: {current_user['email']}")
        
        exam = ExamService.create_exam(
            title=data['title'],
            description=data.get('description', ''),
            created_by_admin=current_user['id'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            duration_minutes=data['duration_minutes'],
            exam_config=data['exam_config']
        )
        
        logger.info(f"Exam created successfully - ID: {exam['id']}, Title: {data['title']}")
        
        return jsonify({
            'message': 'Exam created successfully',
            'exam': exam
        }), 201
        
    except ValueError as e:
        logger.warning(f"Create exam validation error - Admin: {current_user['id']}, Error: {str(e)}")
        return jsonify({
            'error': str(e),
            'error_code': 'EXAM_001'
        }), 400
    except Exception as e:
        log_api_error('/exams', 'POST', e, current_user['id'], data)
        return jsonify({
            'error': 'Exam creation failed',
            'error_code': 'EXAM_002'
        }), 500


@exams_bp.route('', methods=['GET'])
@token_required
@admin_required
def get_all_exams(current_user):
    """
    Get all exams (Admin only).
    
    Query Parameters:
        - status: Filter by status (optional)
        - created_by: Filter by admin UUID (optional)
    
    Returns:
        200: List of exams
    """
    try:
        status = request.args.get('status')
        created_by = request.args.get('created_by')
        
        logger.info(f"Fetching exams - Admin: {current_user['email']}, Status: {status}")
        
        exams = ExamService.get_all_exams_for_admin(
            status=status,
            created_by=created_by
        )
        
        logger.info(f"Retrieved {len(exams)} exams - Admin: {current_user['email']}")
        
        return jsonify({
            'exams': exams,
            'count': len(exams)
        }), 200
        
    except Exception as e:
        log_api_error('/exams', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to retrieve exams',
            'error_code': 'EXAM_003'
        }), 500


@exams_bp.route('/<exam_id>', methods=['GET'])
@token_required
@admin_required
def get_exam_by_id(current_user, exam_id):
    """
    Get exam details with full config (Admin only).
    
    Returns:
        200: Exam details
        404: Exam not found
    """
    try:
        logger.info(f"Fetching exam details - ID: {exam_id}, Admin: {current_user['email']}")
        
        exam = ExamService.get_exam_details(exam_id, include_config=True)
        
        return jsonify({
            'exam': exam
        }), 200
        
    except ValueError as e:
        logger.warning(f"Get exam not found - ID: {exam_id}, Admin: {current_user['id']}")
        return jsonify({
            'error': str(e),
            'error_code': 'EXAM_004'
        }), 404
    except Exception as e:
        log_api_error(f'/exams/{exam_id}', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to retrieve exam',
            'error_code': 'EXAM_005'
        }), 500


@exams_bp.route('/<exam_id>', methods=['PUT'])
@token_required
@admin_required
def update_exam(current_user, exam_id):
    """
    Update exam (Admin only).
    
    Request Body:
        {
            "title": "Updated Title",
            "description": "Updated description",
            "start_time": "2026-01-20T10:00:00",
            "end_time": "2026-01-20T12:00:00",
            "duration_minutes": 120,
            "exam_config": {...}
        }
    
    All fields optional - only provided fields will be updated.
    
    Returns:
        200: Exam updated successfully
        400: Validation error
        404: Exam not found
    """
    try:
        data = request.get_json()
        
        if not data:
            logger.warning(f"Update exam with no data - ID: {exam_id}, Admin: {current_user['id']}")
            return jsonify({
                'error': 'No update data provided',
                'error_code': 'VAL_001'
            }), 400
        
        logger.info(f"Updating exam - ID: {exam_id}, Admin: {current_user['email']}")
        
        # Update exam
        exam = ExamService.update_exam(exam_id, **data)
        
        logger.info(f"Exam updated successfully - ID: {exam_id}")
        
        return jsonify({
            'message': 'Exam updated successfully',
            'exam': exam
        }), 200
        
    except ValueError as e:
        error_msg = str(e)
        status_code = 404 if 'not found' in error_msg.lower() else 400
        logger.warning(f"Update exam error - ID: {exam_id}, Error: {error_msg}")
        return jsonify({
            'error': error_msg,
            'error_code': 'EXAM_006'
        }), status_code
    except Exception as e:
        log_api_error(f'/exams/{exam_id}', 'PUT', e, current_user['id'], data)
        return jsonify({
            'error': 'Exam update failed',
            'error_code': 'EXAM_007'
        }), 500


@exams_bp.route('/<exam_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_exam(current_user, exam_id):
    """
    Delete exam (Admin only).
    
    Returns:
        200: Exam deleted successfully
        404: Exam not found
    """
    try:
        logger.info(f"Deleting exam - ID: {exam_id}, Admin: {current_user['email']}")
        
        ExamService.delete_exam(exam_id)
        
        logger.info(f"Exam deleted successfully - ID: {exam_id}")
        
        return jsonify({
            'message': 'Exam deleted successfully'
        }), 200
        
    except ValueError as e:
        logger.warning(f"Delete exam not found - ID: {exam_id}")
        return jsonify({
            'error': str(e),
            'error_code': 'EXAM_008'
        }), 404
    except Exception as e:
        log_api_error(f'/exams/{exam_id}', 'DELETE', e, current_user['id'])
        return jsonify({
            'error': 'Exam deletion failed',
            'error_code': 'EXAM_009'
        }), 500


@exams_bp.route('/<exam_id>/status', methods=['PATCH'])
@token_required
@admin_required
def change_exam_status(current_user, exam_id):
    """
    Change exam status (Admin only).
    
    Request Body:
        {
            "status": "scheduled"
        }
    
    Valid transitions:
        - draft -> scheduled, cancelled
        - scheduled -> active, cancelled
        - active -> completed, cancelled
        - completed -> (terminal)
        - cancelled -> (terminal)
    
    Returns:
        200: Status updated successfully
        400: Invalid transition
        404: Exam not found
    """
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            logger.warning(f"Change status missing status - ID: {exam_id}, Admin: {current_user['id']}")
            return jsonify({
                'error': 'Status is required',
                'error_code': 'VAL_009'
            }), 400
        
        logger.info(f"Changing exam status - ID: {exam_id}, Status: {data['status']}, Admin: {current_user['email']}")
        
        updated_exam = ExamService.change_status(exam_id, data['status'])
        
        return jsonify({
            'message': f"Exam status changed to {data['status']}",
            'exam': updated_exam
        }), 200
        
    except ValueError as e:
        error_msg = str(e)
        status_code = 404 if 'not found' in error_msg.lower() else 400
        logger.warning(f"Change status error - ID: {exam_id}, Error: {error_msg}")
        return jsonify({
            'error': error_msg,
            'error_code': 'EXAM_010'
        }), status_code
    except Exception as e:
        log_api_error(f'/exams/{exam_id}/status', 'PATCH', e, current_user['id'], data)
        return jsonify({
            'error': 'Status change failed',
            'error_code': 'EXAM_011'
        }), 500


# ============================================
# STUDENT ENDPOINTS
# ============================================

@exams_bp.route('/available', methods=['GET'])
@token_required
@student_required
def get_available_exams(current_user):
    """
    Get available exams for students (assigned exams only with scheduled or active status).
    
    Returns exam list without exam_config (questions hidden).
    Students only see exams that have been assigned to them.
    
    Returns:
        200: List of available assigned exams
    """
    try:
        logger.info(f"Fetching available exams - Student: {current_user['email']}")
        
        from services.exam_assignment_service import ExamAssignmentService
        
        # Get assigned exams for this specific student
        exams = ExamAssignmentService.get_available_exams_for_student(
            student_id=current_user['id']
        )
        
        logger.info(f"Retrieved {len(exams)} available exams - Student: {current_user['email']}")
        
        return jsonify({
            'exams': exams,
            'count': len(exams)
        }), 200
        
    except Exception as e:
        log_api_error('/exams/available', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to retrieve available exams',
            'error_code': 'EXAM_012'
        }), 500


@exams_bp.route('/<exam_id>/details', methods=['GET'])
@token_required
@student_required
def get_exam_details_for_student(current_user, exam_id):
    """
    Get exam details for student (without exam_config).
    
    Students can only view scheduled or active exams.
    
    Returns:
        200: Exam details (without questions)
        403: Exam not available for students
        404: Exam not found
    """
    try:
        logger.info(f"Fetching exam details - ID: {exam_id}, Student: {current_user['email']}")
        
        # Get exam without config
        exam = ExamService.get_exam_details(exam_id, include_config=False)
        
        # Verify exam is available for students
        if exam['status'] not in ['scheduled', 'active']:
            logger.warning(f"Student accessed unavailable exam - ID: {exam_id}, Status: {exam['status']}")
            return jsonify({
                'error': 'This exam is not available for students',
                'error_code': 'EXAM_013'
            }), 403
        
        return jsonify({
            'exam': exam
        }), 200
        
    except ValueError as e:
        logger.warning(f"Student get exam error - ID: {exam_id}: {str(e)}")
        return jsonify({
            'error': str(e),
            'error_code': 'EXAM_014'
        }), 404
    except Exception as e:
        log_api_error(f'/exams/{exam_id}/details', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to retrieve exam details',
            'error_code': 'EXAM_015'
        }), 500
