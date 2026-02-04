"""
Exam Attempts Routes
===================
API endpoints for exam attempt management.

Student Endpoints:
- POST /api/attempts/start - Start new exam attempt
- GET /api/attempts/my-attempts - Get my attempts history
- GET /api/attempts/:id - Get attempt details
- POST /api/attempts/:id/submit - Submit exam answers
"""

from flask import Blueprint, request, jsonify
from services.exam_attempt_service import ExamAttemptService
from middleware.auth_middleware import token_required, student_required
from utils.logger import setup_logger
from utils.error_handlers import validate_required_fields, log_api_error

logger = setup_logger(__name__)

# Create blueprint
attempts_bp = Blueprint('attempts', __name__)


@attempts_bp.route('/start', methods=['POST'])
@token_required
@student_required
def start_attempt(current_user):
    """
    Start a new exam attempt (Student only).
    
    Request Body:
        {
            "exam_id": "uuid",
            "session_data": {
                "ip_address": "127.0.0.1",
                "user_agent": "Mozilla/5.0...",
                "browser": "Chrome"
            }
        }
    
    Returns:
        201: Attempt created with exam config
        400: Validation error
    """
    try:
        data = request.get_json()
        
        if not data:
            logger.warning(f"Start attempt with no data - User: {current_user['id']}")
            return jsonify({
                'error': 'Request body is required',
                'error_code': 'VAL_001'
            }), 400
        
        if not data.get('exam_id'):
            logger.warning(f"Start attempt without exam_id - User: {current_user['id']}")
            return jsonify({
                'error': 'exam_id is required',
                'error_code': 'VAL_006'
            }), 400
        
        logger.info(f"Starting exam attempt - User: {current_user['email']}, Exam: {data['exam_id']}")
        
        attempt = ExamAttemptService.start_attempt(
            exam_id=data['exam_id'],
            student_id=current_user['id'],
            session_data=data.get('session_data')
        )
        
        logger.info(f"Exam attempt started successfully - Attempt ID: {attempt.get('id')}, User: {current_user['email']}")
        
        return jsonify({
            'message': 'Exam attempt started',
            'attempt': attempt
        }), 201
        
    except ValueError as e:
        logger.warning(f"Start attempt validation error - User: {current_user['id']}, Error: {str(e)}")
        return jsonify({
            'error': str(e),
            'error_code': 'ATTEMPT_001'
        }), 400
    except Exception as e:
        log_api_error('/attempts/start', 'POST', e, current_user['id'], data)
        return jsonify({
            'error': 'Failed to start exam attempt',
            'error_code': 'ATTEMPT_002'
        }), 500


@attempts_bp.route('/my-attempts', methods=['GET'])
@token_required
@student_required
def get_my_attempts(current_user):
    """
    Get all my exam attempts (Student only).
    
    Returns:
        200: List of attempts with scores
    """
    try:
        logger.info(f"Fetching attempts - User: {current_user['email']}")
        
        attempts = ExamAttemptService.get_student_attempts(current_user['id'])
        
        logger.info(f"Retrieved {len(attempts)} attempts for user: {current_user['email']}")
        
        return jsonify({
            'attempts': attempts,
            'count': len(attempts)
        }), 200
        
    except Exception as e:
        log_api_error('/attempts/my-attempts', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to get attempts',
            'error_code': 'ATTEMPT_003'
        }), 500


@attempts_bp.route('/<attempt_id>', methods=['GET'])
@token_required
@student_required
def get_attempt_details(current_user, attempt_id):
    """
    Get attempt details (Student only).
    
    Can only view own attempts.
    
    Returns:
        200: Attempt details
        403: Not your attempt
        404: Attempt not found
    """
    try:
        logger.info(f"Fetching attempt details - User: {current_user['email']}, Attempt: {attempt_id}")
        
        attempt = ExamAttemptService.get_attempt_details(
            attempt_id=attempt_id,
            student_id=current_user['id']
        )
        
        logger.info(f"Retrieved attempt details - Attempt: {attempt_id}, User: {current_user['email']}")
        
        return jsonify({
            'attempt': attempt
        }), 200
        
    except ValueError as e:
        error_msg = str(e)
        status_code = 404 if 'not found' in error_msg.lower() else 403
        logger.warning(f"Get attempt details failed - User: {current_user['id']}, Attempt: {attempt_id}, Error: {error_msg}")
        return jsonify({
            'error': error_msg,
            'error_code': 'ATTEMPT_004' if status_code == 404 else 'ATTEMPT_005'
        }), status_code
    except Exception as e:
        log_api_error(f'/attempts/{attempt_id}', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to get attempt details',
            'error_code': 'ATTEMPT_006'
        }), 500


@attempts_bp.route('/<attempt_id>/submit', methods=['POST'])
@token_required
@student_required
def submit_attempt(current_user, attempt_id):
    """
    Submit exam attempt with answers (Student only).
    
    Request Body:
        {
            "answers": {
                "1": "answer_a",
                "2": "answer_b"
            }
        }
    
    Returns:
        200: Submission created with score
        400: Validation error
    """
    try:
        data = request.get_json()
        
        if not data:
            logger.warning(f"Submit attempt with no data - User: {current_user['id']}, Attempt: {attempt_id}")
            return jsonify({
                'error': 'Request body is required',
                'error_code': 'VAL_001'
            }), 400
        
        if not data.get('answers'):
            logger.warning(f"Submit attempt without answers - User: {current_user['id']}, Attempt: {attempt_id}")
            return jsonify({
                'error': 'answers are required',
                'error_code': 'VAL_007'
            }), 400
        
        logger.info(f"Submitting exam - User: {current_user['email']}, Attempt: {attempt_id}, Answers count: {len(data['answers'])}")
        
        submission = ExamAttemptService.submit_attempt(
            attempt_id=attempt_id,
            student_id=current_user['id'],
            answers=data['answers']
        )
        
        logger.info(f"Exam submitted successfully - Attempt: {attempt_id}, User: {current_user['email']}, Score: {submission.get('score')}")
        
        return jsonify({
            'message': 'Exam submitted successfully',
            'submission': submission
        }), 200
        
    except ValueError as e:
        logger.warning(f"Submit attempt validation error - User: {current_user['id']}, Attempt: {attempt_id}, Error: {str(e)}")
        return jsonify({
            'error': str(e),
            'error_code': 'ATTEMPT_007'
        }), 400
    except Exception as e:
        log_api_error(f'/attempts/{attempt_id}/submit', 'POST', e, current_user['id'], data)
        return jsonify({
            'error': 'Failed to submit exam',
            'error_code': 'ATTEMPT_008'
        }), 500


@attempts_bp.route('/<attempt_id>/terminate', methods=['POST'])
@token_required
@student_required
def terminate_attempt(current_user, attempt_id):
    """
    Terminate exam attempt due to proctoring violation (Student only).
    
    This is called automatically when violations like multiple faces,
    tab switches, or window blur are detected.
    
    Request Body:
        {
            "reason": "Multiple persons detected",
            "event_type": "multiple_faces",
            "metadata": {...}
        }
    
    Returns:
        200: Attempt terminated
        400: Validation error
    """
    try:
        data = request.get_json() or {}
        
        reason = data.get('reason', 'Proctoring violation detected')
        event_type = data.get('event_type', 'unknown')
        
        logger.warning(f"Terminating exam due to violation - User: {current_user['email']}, Attempt: {attempt_id}, Reason: {reason}, Event: {event_type}")
        
        # Terminate the attempt
        result = ExamAttemptService.terminate_attempt(
            attempt_id=attempt_id,
            student_id=current_user['id'],
            reason=reason,
            event_type=event_type
        )
        
        logger.info(f"Exam terminated successfully - Attempt: {attempt_id}, Reason: {reason}")
        
        return jsonify({
            'message': 'Exam terminated due to proctoring violation',
            'reason': reason,
            'event_type': event_type,
            'status': 'terminated'
        }), 200
        
    except ValueError as e:
        logger.warning(f"Terminate attempt error - User: {current_user['id']}, Attempt: {attempt_id}, Error: {str(e)}")
        return jsonify({
            'error': str(e),
            'error_code': 'ATTEMPT_009'
        }), 400
    except Exception as e:
        log_api_error(f'/attempts/{attempt_id}/terminate', 'POST', e, current_user['id'], data)
        return jsonify({
            'error': 'Failed to terminate exam',
            'error_code': 'ATTEMPT_010'
        }), 500

