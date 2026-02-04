"""
Blockchain Service
==================
Business logic for blockchain audit trail management.

Handles:
- Immutable block creation
- Hash chain integrity
- Genesis block initialization
- Chain verification

CRITICAL: NO UPDATE OR DELETE OPERATIONS
"""

from models.blockchain_log import BlockchainLog
from utils.blockchain_hasher import BlockchainHasher
from utils.logger import setup_logger
from datetime import datetime

logger = setup_logger(__name__)


class BlockchainService:
    """
    Blockchain service for immutable audit trail.
    
    Ensures:
    - Sequential chain integrity
    - Cryptographic hash linking
    - Tamper-evident logging
    - No modifications to existing blocks
    """
    
    @staticmethod
    def log_event(event_type, entity_type, entity_id=None, payload=None):
        """
        Log an event to the blockchain.
        
        Automatically:
        1. Fetches previous block hash
        2. Generates current block hash
        3. Creates immutable block
        4. Links to blockchain
        
        Args:
            event_type (str): Type of event (e.g., 'exam_attempt_start')
            entity_type (str): Entity type (e.g., 'exam_attempt')
            entity_id (str, optional): UUID of entity
            payload (dict, optional): Event data
            
        Returns:
            dict: Created blockchain block
            
        Raises:
            Exception: If block creation fails
        """
        try:
            # Step 1: Get previous block hash
            previous_block = BlockchainLog.get_latest_block()
            
            if previous_block:
                previous_hash = previous_block['current_hash']
            else:
                # Genesis block - no previous hash
                previous_hash = None
                logger.info("Creating genesis block for blockchain")
            
            # Step 2: Generate current timestamp
            timestamp = datetime.utcnow().isoformat()
            
            # Step 3: Generate current block hash
            current_hash = BlockchainHasher.generate_block_hash(
                previous_hash=previous_hash,
                event_type=event_type,
                entity_type=entity_type,
                entity_id=entity_id,
                payload=payload,
                timestamp=timestamp
            )
            
            # Step 4: Create immutable block
            block = BlockchainLog.create_block(
                previous_hash=previous_hash,
                current_hash=current_hash,
                event_type=event_type,
                entity_type=entity_type,
                entity_id=entity_id,
                payload=payload
            )
            
            logger.info(
                f"Blockchain event logged: {event_type} | "
                f"Entity: {entity_type}:{entity_id} | "
                f"Hash: {current_hash[:16]}..."
            )
            
            return block
            
        except Exception as e:
            logger.error(f"Failed to log blockchain event: {e}")
            raise
    
    @staticmethod
    def initialize_genesis_block():
        """
        Initialize blockchain with genesis block.
        
        Should be called once when system is first deployed.
        Safe to call multiple times (checks if genesis exists).
        
        Returns:
            dict: Genesis block or existing first block
        """
        try:
            # Check if blockchain already has blocks
            existing_block = BlockchainLog.get_latest_block()
            
            if existing_block:
                logger.info("Genesis block already exists")
                return existing_block
            
            # Create genesis block
            genesis_block = BlockchainService.log_event(
                event_type='system_init',
                entity_type='system',
                entity_id=None,
                payload={
                    'system': 'Smart Proctoring System',
                    'version': '1.0',
                    'description': 'Blockchain audit trail initialized',
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            logger.info("Genesis block created successfully")
            return genesis_block
            
        except Exception as e:
            logger.error(f"Failed to initialize genesis block: {e}")
            raise
    
    @staticmethod
    def get_entity_audit_trail(entity_type, entity_id):
        """
        Get complete audit trail for an entity.
        
        Args:
            entity_type (str): Entity type
            entity_id (str): Entity UUID
            
        Returns:
            dict: Audit trail with blocks and verification
        """
        try:
            # Get blockchain for entity
            blocks = BlockchainLog.get_chain_by_entity(entity_type, entity_id)
            
            # Verify chain integrity
            verification = BlockchainHasher.verify_chain_integrity(blocks)
            
            return {
                'entity_type': entity_type,
                'entity_id': entity_id,
                'total_events': len(blocks),
                'blocks': blocks,
                'verification': verification
            }
            
        except Exception as e:
            logger.error(f"Failed to get audit trail for {entity_type}:{entity_id}: {e}")
            raise
    
    @staticmethod
    def verify_blockchain_integrity(limit=1000):
        """
        Verify integrity of entire blockchain.
        
        Checks:
        - Hash validity for each block
        - Chain link integrity
        
        Args:
            limit (int): Max blocks to verify (performance limit)
            
        Returns:
            dict: Verification result
        """
        try:
            # Get recent blocks in chronological order
            all_blocks = BlockchainLog.get_all_blocks(limit=limit, offset=0)
            
            # Reverse to get chronological order (oldest first)
            all_blocks.reverse()
            
            # Verify chain
            verification = BlockchainHasher.verify_chain_integrity(all_blocks)
            
            logger.info(
                f"Blockchain verification: {verification['message']} | "
                f"Verified: {verification['verified_blocks']}/{verification['total_blocks']}"
            )
            
            return verification
            
        except Exception as e:
            logger.error(f"Failed to verify blockchain integrity: {e}")
            raise
    
    @staticmethod
    def get_blockchain_summary():
        """
        Get blockchain statistics.
        
        Returns:
            dict: Summary statistics
        """
        try:
            total_blocks = BlockchainLog.count_blocks()
            latest_block = BlockchainLog.get_latest_block()
            
            return {
                'total_blocks': total_blocks,
                'latest_block': latest_block,
                'blockchain_initialized': total_blocks > 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get blockchain summary: {e}")
            raise
    
    @staticmethod
    def get_events_by_type(event_type, limit=100):
        """
        Get blockchain events by type.
        
        Args:
            event_type (str): Event type to filter
            limit (int): Max events to return
            
        Returns:
            list: Blockchain blocks of specified type
        """
        try:
            blocks = BlockchainLog.get_blocks_by_event_type(event_type, limit=limit)
            return blocks
            
        except Exception as e:
            logger.error(f"Failed to get events by type {event_type}: {e}")
            raise
    
    # =========================================================================
    # IMMUTABILITY ENFORCEMENT
    # =========================================================================
    # 
    # This service intentionally does NOT provide:
    # - update_block() method
    # - delete_block() method
    # - modify_chain() method
    #
    # Blockchain immutability is enforced at service layer.
    # Any corrections must be done via compensating events.
    # =========================================================================


# =========================================================================
# EVENT TYPE CONSTANTS
# =========================================================================

class BlockchainEvents:
    """
    Standard event types for blockchain logging.
    
    Use these constants to ensure consistency.
    """
    # System events
    SYSTEM_INIT = 'system_init'
    
    # Exam attempt events
    EXAM_ATTEMPT_START = 'exam_attempt_start'
    EXAM_ATTEMPT_SUBMIT = 'exam_attempt_submit'
    EXAM_ATTEMPT_TIMEOUT = 'exam_attempt_timeout'
    EXAM_ATTEMPT_TERMINATE = 'exam_attempt_terminate'
    
    # Proctoring events
    PROCTORING_SUSPICIOUS = 'proctoring_suspicious_event'
    PROCTORING_VIOLATION = 'proctoring_violation_detected'
    
    # AI analysis events
    AI_ANALYSIS_HIGH_RISK = 'ai_analysis_high_risk'
    AI_ANALYSIS_COMPLETED = 'ai_analysis_completed'
    
    # Submission events
    SUBMISSION_CREATED = 'submission_created'
    SUBMISSION_FINALIZED = 'submission_finalized'
    
    # Admin events
    EXAM_PUBLISHED = 'exam_published'
    EXAM_STATUS_CHANGED = 'exam_status_changed'
    USER_CREATED = 'user_created'
    USER_ROLE_CHANGED = 'user_role_changed'


# =========================================================================
# ENTITY TYPE CONSTANTS
# =========================================================================

class BlockchainEntities:
    """
    Standard entity types for blockchain logging.
    """
    SYSTEM = 'system'
    EXAM = 'exam'
    EXAM_ATTEMPT = 'exam_attempt'
    SUBMISSION = 'submission'
    USER = 'user'
    PROCTORING_LOG = 'proctoring_log'
    AI_ANALYSIS = 'ai_analysis'
