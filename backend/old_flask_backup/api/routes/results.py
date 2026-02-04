"""
Results & Submissions Routes
============================
API endpoints for viewing exam results.

Student Endpoints:
- GET /api/results/my-results - Get my exam results
- GET /api/results/:attempt_id/detailed - Get detailed result with answers
"""

from flask import Blueprint, request, jsonify
from services.exam_attempt_service import ExamAttemptService
from models.submission import Submission
from middleware.auth_middleware import token_required, student_required
from utils.logger import setup_logger
from utils.error_handlers import log_api_error

logger = setup_logger(__name__)

# Create blueprint
results_bp = Blueprint('results', __name__)


@results_bp.route('/my-results', methods=['GET'])
@token_required
@student_required
def get_my_results(current_user):
    """
    Get all my exam results (Student only).
    
    Returns:
        200: List of results with scores
    """
    try:
        logger.info(f"Fetching results - User: {current_user['email']}")
        
        results = Submission.find_by_student(current_user['id'])
        
        logger.info(f"Retrieved {len(results)} results for user: {current_user['email']}")
        
        return jsonify(results), 200
        
    except Exception as e:
        log_api_error('/results/my-results', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to get results',
            'error_code': 'RESULT_001'
        }), 500


@results_bp.route('/<attempt_id>/detailed', methods=['GET'])
@token_required
@student_required
def get_detailed_result(current_user, attempt_id):
    """
    Get detailed result for an attempt (Student only).
    
    Includes answers, correct answers, and score breakdown.
    Can only view own results.
    
    Returns:
        200: Detailed result
        403: Not your result
        404: Result not found
    """
    try:
        logger.info(f"Fetching detailed result - User: {current_user['email']}, Attempt: {attempt_id}")
        
        attempt = ExamAttemptService.get_attempt_details(
            attempt_id=attempt_id,
            student_id=current_user['id']
        )
        
        submission = Submission.find_by_attempt(attempt_id)
        
        if not submission:
            logger.warning(f"Result not found - Attempt: {attempt_id}, User: {current_user['id']}")
            return jsonify({
                'error': 'Result not found for this attempt',
                'error_code': 'RESULT_002'
            }), 404
        
        result = {
            'attempt': attempt,
            'submission': submission,
            'score': submission.get('score'),
            'answers': submission.get('answers'),
            'correct_answers': submission.get('correct_answers'),
            'feedback': submission.get('feedback')
        }
        
        logger.info(f"Retrieved detailed result - Attempt: {attempt_id}, Score: {submission.get('score')}")
        
        return jsonify(result), 200
        
    except ValueError as e:
        error_msg = str(e)
        status_code = 404 if 'not found' in error_msg.lower() else 403
        logger.warning(f"Get detailed result failed - Attempt: {attempt_id}, User: {current_user['id']}, Error: {error_msg}")
        return jsonify({
            'error': error_msg,
            'error_code': 'RESULT_003'
        }), status_code
    except Exception as e:
        log_api_error(f'/results/{attempt_id}/detailed', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to get detailed results',
            'error_code': 'RESULT_004'
        }), 500
