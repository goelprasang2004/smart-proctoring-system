"""
Exam Assignment Routes
======================
API endpoints for managing exam-to-student assignments.

Admin Endpoints:
- POST /api/exams/:exam_id/assign - Assign exam to students
- GET /api/exams/:exam_id/assignments - Get assigned students
- DELETE /api/exams/:exam_id/assign/:student_id - Remove assignment
- GET /api/students/:student_id/assigned-exams - Get student's assignments
"""

from flask import Blueprint, request, jsonify
from services.exam_assignment_service import ExamAssignmentService
from middleware.auth_middleware import token_required, admin_required
from middleware.rate_limit import rate_limit, RateLimits
from utils.logger import setup_logger
from utils.error_handlers import log_api_error

logger = setup_logger(__name__)

# Create blueprint
exam_assignments_bp = Blueprint('exam_assignments', __name__)


# ============================================
# ADMIN ENDPOINTS
# ============================================

@exam_assignments_bp.route('/<exam_id>/assign', methods=['POST'])
@token_required
@admin_required
@rate_limit(**RateLimits.GENERAL)
def assign_exam_to_students(current_user, exam_id):
    """
    Assign exam to one or more students (Admin only).
    
    Request Body:
        {
            "student_ids": ["uuid1", "uuid2", "uuid3"]
        }
    
    Returns:
        200: Assignment results with success/failed lists
        400: Validation error
        404: Exam not found
    """
    try:
        data = request.get_json()
        
        if not data:
            logger.warning(f"Assign exam with no data - Admin: {current_user['id']}")
            return jsonify({
                'error': 'Request body is required',
                'error_code': 'VAL_001'
            }), 400
        
        # Validate required fields
        if 'student_ids' not in data:
            return jsonify({
                'error': 'Missing required field: student_ids',
                'error_code': 'VAL_010'
            }), 400
        
        student_ids = data['student_ids']
        
        # Validate student_ids is a list
        if not isinstance(student_ids, list):
            return jsonify({
                'error': 'student_ids must be an array',
                'error_code': 'VAL_011'
            }), 400
        
        if len(student_ids) == 0:
            return jsonify({
                'error': 'student_ids cannot be empty',
                'error_code': 'VAL_012'
            }), 400
        
        logger.info(f"Assigning exam {exam_id} to {len(student_ids)} students - Admin: {current_user['email']}")
        
        # Assign exam to students
        result = ExamAssignmentService.assign_exam_to_students(
            exam_id=exam_id,
            student_ids=student_ids,
            assigned_by_admin=current_user['id']
        )
        
        response = {
            'message': f"Assigned to {len(result['success'])} student(s)",
            'success': result['success'],
            'failed': result['failed'],
            'total_requested': len(student_ids),
            'total_success': len(result['success']),
            'total_failed': len(result['failed'])
        }
        
        logger.info(
            f"Admin {current_user['email']} assigned exam {exam_id} - "
            f"Success: {len(result['success'])}, Failed: {len(result['failed'])}"
        )
        
        return jsonify(response), 200
        
    except ValueError as e:
        error_msg = str(e)
        status_code = 404 if 'not found' in error_msg.lower() else 400
        logger.warning(f"Assign exam error - Exam: {exam_id}, Error: {error_msg}")
        return jsonify({
            'error': error_msg,
            'error_code': 'ASSIGN_001'
        }), status_code
    except Exception as e:
        log_api_error(f'/exams/{exam_id}/assign', 'POST', e, current_user['id'], data)
        return jsonify({
            'error': 'Assignment failed',
            'error_code': 'ASSIGN_002'
        }), 500


@exam_assignments_bp.route('/<exam_id>/assignments', methods=['GET'])
@token_required
@admin_required
def get_exam_assignments(current_user, exam_id):
    """
    Get all students assigned to an exam (Admin only).
    
    Returns:
        200: List of assigned students
        404: Exam not found
    """
    try:
        logger.info(f"Fetching assignments for exam {exam_id} - Admin: {current_user['email']}")
        
        assignments = ExamAssignmentService.get_exam_assignments(exam_id)
        
        return jsonify({
            'exam_id': exam_id,
            'assignments': assignments,
            'count': len(assignments)
        }), 200
        
    except ValueError as e:
        logger.warning(f"Get assignments exam not found - Exam: {exam_id}")
        return jsonify({
            'error': str(e),
            'error_code': 'ASSIGN_003'
        }), 404
    except Exception as e:
        log_api_error(f'/exams/{exam_id}/assignments', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to retrieve assignments',
            'error_code': 'ASSIGN_004'
        }), 500


@exam_assignments_bp.route('/<exam_id>/assign/<student_id>', methods=['DELETE'])
@token_required
@admin_required
def remove_exam_assignment(current_user, exam_id, student_id):
    """
    Remove exam assignment from a student (Admin only).
    
    Returns:
        200: Assignment removed successfully
        404: Assignment, exam, or student not found
    """
    try:
        logger.info(f"Removing assignment - Exam: {exam_id}, Student: {student_id}, Admin: {current_user['email']}")
        
        ExamAssignmentService.remove_assignment(exam_id, student_id)
        
        logger.info(
            f"Admin {current_user['email']} removed assignment: "
            f"exam {exam_id} from student {student_id}"
        )
        
        return jsonify({
            'message': 'Assignment removed successfully'
        }), 200
        
    except ValueError as e:
        logger.warning(f"Remove assignment error - {str(e)}")
        return jsonify({
            'error': str(e),
            'error_code': 'ASSIGN_005'
        }), 404
    except Exception as e:
        log_api_error(f'/exams/{exam_id}/assign/{student_id}', 'DELETE', e, current_user['id'])
        return jsonify({
            'error': 'Failed to remove assignment',
            'error_code': 'ASSIGN_006'
        }), 500


@exam_assignments_bp.route('/students/<student_id>/assigned-exams', methods=['GET'])
@token_required
@admin_required
def get_student_assigned_exams(current_user, student_id):
    """
    Get all exams assigned to a specific student (Admin only).
    
    This is for admin view to see what exams a student has been assigned.
    
    Returns:
        200: List of assigned exams
        404: Student not found
    """
    try:
        logger.info(f"Fetching assignments for student {student_id} - Admin: {current_user['email']}")
        
        exams = ExamAssignmentService.get_student_assigned_exams(student_id)
        
        return jsonify({
            'student_id': student_id,
            'assigned_exams': exams,
            'count': len(exams)
        }), 200
        
    except ValueError as e:
        logger.warning(f"Get student assignments error - Student: {student_id}, Error: {str(e)}")
        return jsonify({
            'error': str(e),
            'error_code': 'ASSIGN_007'
        }), 404
    except Exception as e:
        log_api_error(f'/students/{student_id}/assigned-exams', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to retrieve student assignments',
            'error_code': 'ASSIGN_008'
        }), 500
