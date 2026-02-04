"""
Blockchain Routes
=================
API endpoints for blockchain audit trail management.

Admin-only endpoints for:
- Viewing blockchain logs
- Verifying chain integrity
- Getting audit trails
- Blockchain statistics
"""

from flask import Blueprint, request, jsonify
from services.blockchain_service import BlockchainService, BlockchainEvents, BlockchainEntities
from middleware.auth_middleware import token_required, admin_required
from utils.logger import setup_logger
from utils.error_handlers import log_api_error

logger = setup_logger(__name__)

# Create blueprint
blockchain_bp = Blueprint('blockchain', __name__)


# ============================================
# ADMIN ENDPOINTS (Read-Only)
# ============================================

@blockchain_bp.route('/summary', methods=['GET'])
@token_required
@admin_required
def get_blockchain_summary(current_user):
    """
    Get blockchain statistics (Admin only).
    
    Returns:
        200: Blockchain summary
    """
    try:
        logger.info(f"Fetching blockchain summary - Admin: {current_user['email']}")
        
        summary = BlockchainService.get_blockchain_summary()
        
        return jsonify({
            'summary': summary
        }), 200
        
    except Exception as e:
        log_api_error('/blockchain/summary', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to get blockchain summary',
            'error_code': 'CHAIN_001'
        }), 500


@blockchain_bp.route('/verify', methods=['GET'])
@token_required
@admin_required
def verify_blockchain_integrity(current_user):
    """
    Verify blockchain integrity (Admin only).
    
    Checks:
    - Hash validity for each block
    - Chain link integrity
    
    Query Parameters:
        - limit: Max blocks to verify (default: 1000)
    
    Returns:
        200: Verification result
    """
    try:
        limit = int(request.args.get('limit', 1000))
        logger.info(f"Verifying blockchain integrity (limit: {limit}) - Admin: {current_user['email']}")
        
        verification = BlockchainService.verify_blockchain_integrity(limit=limit)
        
        return jsonify({
            'verification': verification
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': str(e),
            'error_code': 'CHAIN_002'
        }), 400
    except Exception as e:
        log_api_error('/blockchain/verify', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to verify blockchain',
            'error_code': 'CHAIN_003'
        }), 500


@blockchain_bp.route('/entity/<entity_type>/<entity_id>', methods=['GET'])
@token_required
@admin_required
def get_entity_audit_trail(current_user, entity_type, entity_id):
    """
    Get complete audit trail for an entity (Admin only).
    
    Args:
        entity_type: Entity type (e.g., 'exam_attempt')
        entity_id: Entity UUID
    
    Returns:
        200: Audit trail with blocks and verification
        404: No blocks found
    """
    try:
        logger.info(f"Fetching audit trail - Entity: {entity_type}, ID: {entity_id}, Admin: {current_user['email']}")
        
        audit_trail = BlockchainService.get_entity_audit_trail(entity_type, entity_id)
        
        if audit_trail['total_events'] == 0:
            logger.info(f"No blockchain events found - Entity: {entity_id}")
            return jsonify({
                'message': 'No blockchain events found for this entity',
                'entity_type': entity_type,
                'entity_id': entity_id,
                'audit_trail': audit_trail
            }), 200  # Return 200 with empty trail instead of 404
        
        return jsonify({
            'audit_trail': audit_trail
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': str(e),
            'error_code': 'CHAIN_004'
        }), 400
    except Exception as e:
        log_api_error(f'/blockchain/entity/{entity_type}/{entity_id}', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to get audit trail',
            'error_code': 'CHAIN_005'
        }), 500


@blockchain_bp.route('/events/<event_type>', methods=['GET'])
@token_required
@admin_required
def get_events_by_type(current_user, event_type):
    """
    Get blockchain events by type (Admin only).
    
    Args:
        event_type: Event type to filter
    
    Query Parameters:
        - limit: Max events to return (default: 100)
    
    Returns:
        200: List of blockchain blocks
    """
    try:
        limit = int(request.args.get('limit', 100))
        logger.info(f"Fetching events by type: {event_type} - Admin: {current_user['email']}")
        
        blocks = BlockchainService.get_events_by_type(event_type, limit=limit)
        
        return jsonify({
            'event_type': event_type,
            'blocks': blocks,
            'count': len(blocks)
        }), 200
        
    except Exception as e:
        log_api_error(f'/blockchain/events/{event_type}', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to get events',
            'error_code': 'CHAIN_006'
        }), 500


@blockchain_bp.route('/attempt/<attempt_id>', methods=['GET'])
@token_required
@admin_required
def get_attempt_audit_trail(current_user, attempt_id):
    """
    Get blockchain audit trail for exam attempt (Admin only).
    
    Convenience endpoint specifically for exam attempts.
    
    Args:
        attempt_id: Exam attempt UUID
    
    Returns:
        200: Audit trail for attempt
    """
    try:
        logger.info(f"Fetching attempt audit trail - Attempt: {attempt_id}, Admin: {current_user['email']}")
        
        audit_trail = BlockchainService.get_entity_audit_trail(
            entity_type=BlockchainEntities.EXAM_ATTEMPT,
            entity_id=attempt_id
        )
        
        return jsonify({
            'audit_trail': audit_trail
        }), 200
        
    except Exception as e:
        log_api_error(f'/blockchain/attempt/{attempt_id}', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to get attempt audit trail',
            'error_code': 'CHAIN_007'
        }), 500


@blockchain_bp.route('/initialize', methods=['POST'])
@token_required
@admin_required
def initialize_genesis_block(current_user):
    """
    Initialize blockchain with genesis block (Admin only).
    
    Safe to call multiple times (checks if genesis exists).
    Should be called once during system setup.
    
    Returns:
        201: Genesis block created or already exists
    """
    try:
        logger.info(f"Initializing genesis block - Admin: {current_user['email']}")
        
        genesis_block = BlockchainService.initialize_genesis_block()
        
        return jsonify({
            'message': 'Blockchain initialized',
            'genesis_block': genesis_block
        }), 201
        
    except Exception as e:
        log_api_error('/blockchain/initialize', 'POST', e, current_user['id'])
        return jsonify({
            'error': 'Failed to initialize blockchain',
            'error_code': 'CHAIN_008'
        }), 500


# ============================================
# HELPER ENDPOINT: List Available Event Types
# ============================================

@blockchain_bp.route('/event-types', methods=['GET'])
@token_required
@admin_required
def get_event_types(current_user):
    """
    Get list of standard blockchain event types (Admin only).
    
    Returns:
        200: List of event types
    """
    try:
        event_types = {
            'system': [
                BlockchainEvents.SYSTEM_INIT
            ],
            'exam_attempts': [
                BlockchainEvents.EXAM_ATTEMPT_START,
                BlockchainEvents.EXAM_ATTEMPT_SUBMIT,
                BlockchainEvents.EXAM_ATTEMPT_TIMEOUT,
                BlockchainEvents.EXAM_ATTEMPT_TERMINATE
            ],
            'proctoring': [
                BlockchainEvents.PROCTORING_SUSPICIOUS,
                BlockchainEvents.PROCTORING_VIOLATION
            ],
            'ai_analysis': [
                BlockchainEvents.AI_ANALYSIS_HIGH_RISK,
                BlockchainEvents.AI_ANALYSIS_COMPLETED
            ],
            'submissions': [
                BlockchainEvents.SUBMISSION_CREATED,
                BlockchainEvents.SUBMISSION_FINALIZED
            ],
            'admin': [
                BlockchainEvents.EXAM_PUBLISHED,
                BlockchainEvents.EXAM_STATUS_CHANGED,
                BlockchainEvents.USER_CREATED,
                BlockchainEvents.USER_ROLE_CHANGED
            ]
        }
        
        return jsonify({
            'event_types': event_types
        }), 200
        
    except Exception as e:
        log_api_error('/blockchain/event-types', 'GET', e, current_user['id'])
        return jsonify({
            'error': 'Failed to get event types',
            'error_code': 'CHAIN_009'
        }), 500
