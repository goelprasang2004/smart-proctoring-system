"""
Proctoring Routes
=================
API endpoints for proctoring event logging and monitoring.

Student Endpoints:
- POST /api/proctoring/event - Log proctoring event
- GET /api/proctoring/my-attempt/:attempt_id - Get my proctoring data

Admin Endpoints:
- GET /api/proctoring/attempt/:attempt_id - Get attempt proctoring (admin)
- GET /api/proctoring/suspicious - Get all suspicious attempts
"""

from flask import Blueprint, request, jsonify
from services.proctoring_service import ProctoringService
from middleware.auth_middleware import token_required, student_required, admin_required
from utils.logger import setup_logger
from utils.error_handlers import log_api_error

logger = setup_logger(__name__)

# Create blueprint
proctoring_bp = Blueprint('proctoring', __name__)


# ============================================
# STUDENT ENDPOINTS
# ============================================

@proctoring_bp.route('/event', methods=['POST'])
@token_required
@student_required
def log_proctoring_event(current_user):
    """
    Log a proctoring event during exam (Student only).
    
    Request Body:
        {
            "attempt_id": "uuid",
            "event_type": "tab_switch",
            "description": "Student switched to another tab",
            "metadata": {
                "timestamp": "...",
                "occurrence_count": 3
            }
        }
    
    Event Types:
        - face_detection
        - voice_detection
        - stress_alert
        - tab_switch
        - window_blur
        - multiple_faces
        - no_face
        - suspicious_behavior
    
    Returns:
        201: Event logged successfully
        400: Validation error
    """
    try:
        data = request.get_json()
        
        if not data:
            logger.warning(f"Log event with no data - User: {current_user['id']}")
            return jsonify({
                'error': 'Request body is required',
                'error_code': 'VAL_001'
            }), 400
        
        # Validate required fields
        required_fields = ['attempt_id', 'event_type', 'description']
        missing_fields = [f for f in required_fields if f not in data or not data[f]]
        
        if missing_fields:
            logger.warning(f"Log event missing fields: {missing_fields} - User: {current_user['id']}")
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}',
                'error_code': 'VAL_013'
            }), 400
        
        logger.info(f"Logging proctoring event - User: {current_user['email']}, Event: {data['event_type']}")
        
        # Log event with AI simulation
        event = ProctoringService.log_event(
            attempt_id=data['attempt_id'],
            event_type=data['event_type'],
            description=data['description'],
            metadata=data.get('metadata')
        )
        
        return jsonify({
            'message': 'Proctoring event logged successfully',
            'event': event
        }), 201
        
    except ValueError as e:
        logger.warning(f"Log event error - User: {current_user['id']}: {str(e)}")
        return jsonify({
            'error': str(e),
            'error_code': 'PROCTOR_001'
        }), 400
    except Exception as e:
        log_api_error('/proctoring/event', 'POST', e, current_user['id'], data)
        return jsonify({
            'error': 'Failed to log proctoring event',
            'error_code': 'PROCTOR_002'
        }), 500


@proctoring_bp.route('/my-attempt/<attempt_id>', methods=['GET'])
@token_required
@student_required
def get_my_proctoring_data(current_user, attempt_id):
    """
    Get proctoring data for my exam attempt (Student only).
    
    Students can only view their own attempt data.
    Returns event summary without detailed AI analysis.
    
    Returns:
        200: Proctoring summary
        403: Not your attempt
        404: Attempt not found
    """
    try:
        logger.info(f"Fetching proctoring data summary - User: {current_user['email']}, Attempt: {attempt_id}")
        
        # Verify attempt belongs to current user
        from models.exam_attempt import ExamAttempt
        attempt = ExamAttempt.find_by_id(attempt_id)
        if not attempt:
            logger.warning(f"Attempt not found - Attempt: {attempt_id}")
            return jsonify({
                'error': 'Attempt not found',
                'error_code': 'PROCTOR_010'
            }), 404
        
        if str(attempt['student_id']) != str(current_user['id']):
            logger.warning(f"Access denied - User: {current_user['id']} attempted to access attempt {attempt_id} belonging to {attempt['student_id']}")
            return jsonify({
                'error': 'You do not have permission to view this attempt',
                'error_code': 'AUTH_003'
            }), 403
        
        summary = ProctoringService.get_proctoring_summary(attempt_id)
        
        # Remove sensitive AI details for student view
        if 'ai_summary' in summary:
            summary['ai_summary'] = {
                'total_analyses': summary['ai_summary']['total_analyses']
            }
        
        return jsonify({
            'summary': summary
        }), 200
        
    except ValueError as e:
        logger.warning(f"Proctoring data not found - Attempt: {attempt_id}")
        return jsonify({
            'error': str(e),
            'error_code': 'PROCTOR_003'
        }), 404
    except Exception as e:
        log_api_error(f'/proctoring/my-attempt/{attempt_id}', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to retrieve proctoring data',
            'error_code': 'PROCTOR_004'
        }), 500


# ============================================
# ADMIN ENDPOINTS
# ============================================

@proctoring_bp.route('/attempt/<attempt_id>', methods=['GET'])
@token_required
@admin_required
def get_attempt_proctoring(current_user, attempt_id):
    """
    Get complete proctoring data for an attempt (Admin only).
    
    Includes:
    - All proctoring events
    - AI analysis results
    - Risk assessment
    - Recommendations
    
    Returns:
        200: Complete proctoring data
        404: Attempt not found
    """
    try:
        logger.info(f"Fetching attempt proctoring full data - Admin: {current_user['email']}, Attempt: {attempt_id}")
        
        # Get comprehensive summary
        summary = ProctoringService.get_proctoring_summary(attempt_id)
        
        # Get all events
        events = ProctoringService.get_attempt_events(attempt_id)
        
        # Get all AI analyses
        ai_analyses = ProctoringService.get_attempt_ai_analysis(attempt_id)
        
        # Get suspicious events
        suspicious_events = ProctoringService.get_suspicious_events(attempt_id)
        
        return jsonify({
            'summary': summary,
            'total_events': len(events),
            'events': events,
            'ai_analyses': ai_analyses,
            'suspicious_events': suspicious_events
        }), 200
        
    except ValueError as e:
        logger.warning(f"Admin attempt proctoring not found - Attempt: {attempt_id}")
        return jsonify({
            'error': str(e),
            'error_code': 'PROCTOR_005'
        }), 404
    except Exception as e:
        log_api_error(f'/proctoring/attempt/{attempt_id}', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to retrieve proctoring data',
            'error_code': 'PROCTOR_006'
        }), 500


@proctoring_bp.route('/attempt/<attempt_id>/events', methods=['GET'])
@token_required
@admin_required
def get_attempt_events(current_user, attempt_id):
    """
    Get all proctoring events for an attempt (Admin only).
    
    Query Parameters:
        - event_type: Filter by event type (optional)
    
    Returns:
        200: List of events
    """
    try:
        event_type = request.args.get('event_type')
        logger.info(f"Fetching attempt events - Admin: {current_user['email']}, Attempt: {attempt_id}")
        
        events = ProctoringService.get_attempt_events(
            attempt_id=attempt_id,
            event_type=event_type
        )
        
        return jsonify({
            'attempt_id': attempt_id,
            'event_type_filter': event_type,
            'events': events,
            'count': len(events)
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        log_api_error(f'/proctoring/attempt/{attempt_id}/events', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to retrieve events',
            'error_code': 'PROCTOR_007'
        }), 500


@proctoring_bp.route('/attempt/<attempt_id>/ai-analysis', methods=['GET'])
@token_required
@admin_required
def get_attempt_ai_analysis(current_user, attempt_id):
    """
    Get AI analysis results for an attempt (Admin only).
    
    Query Parameters:
        - analysis_type: Filter by analysis type (optional)
    
    Returns:
        200: List of AI analyses
    """
    try:
        analysis_type = request.args.get('analysis_type')
        logger.info(f"Fetching AI analysis - Admin: {current_user['email']}, Attempt: {attempt_id}")
        
        analyses = ProctoringService.get_attempt_ai_analysis(
            attempt_id=attempt_id,
            analysis_type=analysis_type
        )
        
        return jsonify({
            'attempt_id': attempt_id,
            'analysis_type_filter': analysis_type,
            'analyses': analyses,
            'count': len(analyses)
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        log_api_error(f'/proctoring/attempt/{attempt_id}/ai-analysis', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to retrieve AI analysis',
            'error_code': 'PROCTOR_008'
        }), 500


@proctoring_bp.route('/suspicious', methods=['GET'])
@token_required
@admin_required
def get_all_suspicious_attempts(current_user):
    """
    Get all attempts with suspicious activity (Admin only).
    
    Query Parameters:
        - confidence_threshold: Minimum confidence (default: 0.7)
        - min_event_count: Minimum events (default: 5)
    
    Returns:
        200: List of suspicious attempts
    """
    try:
        from models.proctoring import ProctoringEvent
        
        confidence_threshold = float(request.args.get('confidence_threshold', 0.3))
        min_event_count = int(request.args.get('min_event_count', 1))
        
        logger.info(f"Fetching suspicious attempts - Admin: {current_user['email']}")
        
        suspicious_attempts = ProctoringEvent.get_all_suspicious_attempts(
            confidence_threshold=confidence_threshold,
            min_event_count=min_event_count
        )
        
        return jsonify({
            'suspicious_attempts': suspicious_attempts,
            'count': len(suspicious_attempts),
            'filters': {
                'confidence_threshold': confidence_threshold,
                'min_event_count': min_event_count
            }
        }), 200
        
    except Exception as e:
        log_api_error('/proctoring/suspicious', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to retrieve suspicious attempts',
            'error_code': 'PROCTOR_009'
        }), 500
