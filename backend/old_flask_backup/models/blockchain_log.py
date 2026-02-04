"""
Blockchain Log Model
====================
Data access layer for blockchain-inspired audit logging.

This module provides APPEND-ONLY operations for the blockchain_logs table.
Implements immutable, hash-linked audit trail for critical system events.

WARNING: NO UPDATE OR DELETE OPERATIONS ALLOWED
"""

from models.database import get_db_cursor
from utils.logger import setup_logger
import json

logger = setup_logger(__name__)


class BlockchainLog:
    """
    Blockchain log model for immutable audit trail.
    
    Core Principles:
    - Append-only (no updates, no deletes)
    - Hash-linked chain
    - Cryptographically verifiable
    - Tamper-evident
    """
    
    @staticmethod
    def create_block(previous_hash, current_hash, event_type, entity_type, 
                     entity_id=None, payload=None):
        """
        Create a new blockchain log entry (block).
        
        IMMUTABLE: Once created, cannot be modified or deleted.
        
        Args:
            previous_hash (str): Hash of previous block (None for genesis)
            current_hash (str): SHA-256 hash of current block
            event_type (str): Type of event (e.g., 'exam_attempt_start')
            entity_type (str): Entity type (e.g., 'exam_attempt', 'submission')
            entity_id (str, optional): UUID of related entity
            payload (dict, optional): Event data (JSONB)
            
        Returns:
            dict: Created blockchain block
            
        Raises:
            Exception: If block creation fails
        """
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    INSERT INTO blockchain_logs (
                        previous_hash, current_hash, event_type, 
                        entity_type, entity_id, payload
                    )
                    VALUES (%s, %s, %s, %s, %s::uuid, %s::jsonb)
                    RETURNING id, previous_hash, current_hash, event_type, 
                              entity_type, entity_id, payload, created_at;
                """, (previous_hash, current_hash, event_type, 
                      entity_type, entity_id, json.dumps(payload) if payload else None))
                
                block = cursor.fetchone()
                
                logger.info(f"Blockchain block created: {event_type} (hash: {current_hash[:16]}...)")
                
                return {
                    'id': str(block[0]),
                    'previous_hash': block[1],
                    'current_hash': block[2],
                    'event_type': block[3],
                    'entity_type': block[4],
                    'entity_id': str(block[5]) if block[5] else None,
                    'payload': block[6],
                    'created_at': block[7].isoformat() if block[7] else None
                }
                
        except Exception as e:
            logger.error(f"Failed to create blockchain block: {e}")
            raise
    
    @staticmethod
    def get_latest_block():
        """
        Get the most recent blockchain block.
        
        Used to obtain previous_hash for next block in chain.
        
        Returns:
            dict: Latest block
            None: If blockchain is empty (genesis block needed)
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT id, previous_hash, current_hash, event_type, 
                           entity_type, entity_id, payload, created_at
                    FROM blockchain_logs
                    ORDER BY created_at DESC, id DESC
                    LIMIT 1;
                """)
                
                block = cursor.fetchone()
                
                if not block:
                    return None
                
                return {
                    'id': str(block[0]),
                    'previous_hash': block[1],
                    'current_hash': block[2],
                    'event_type': block[3],
                    'entity_type': block[4],
                    'entity_id': str(block[5]) if block[5] else None,
                    'payload': block[6],
                    'created_at': block[7].isoformat() if block[7] else None
                }
                
        except Exception as e:
            logger.error(f"Failed to get latest block: {e}")
            raise
    
    @staticmethod
    def get_chain_by_entity(entity_type, entity_id):
        """
        Get blockchain chain for specific entity.
        
        Args:
            entity_type (str): Entity type (e.g., 'exam_attempt')
            entity_id (str): Entity UUID
            
        Returns:
            list: Blockchain blocks for entity (chronological order)
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT id, previous_hash, current_hash, event_type, 
                           entity_type, entity_id, payload, created_at
                    FROM blockchain_logs
                    WHERE entity_type = %s
                    AND entity_id = %s::uuid
                    ORDER BY created_at ASC, id ASC;
                """, (entity_type, entity_id))
                
                blocks = cursor.fetchall()
                
                return [{
                    'id': str(block[0]),
                    'previous_hash': block[1],
                    'current_hash': block[2],
                    'event_type': block[3],
                    'entity_type': block[4],
                    'entity_id': str(block[5]) if block[5] else None,
                    'payload': block[6],
                    'created_at': block[7].isoformat() if block[7] else None
                } for block in blocks]
                
        except Exception as e:
            logger.error(f"Failed to get chain for {entity_type}:{entity_id}: {e}")
            raise
    
    @staticmethod
    def get_all_blocks(limit=100, offset=0):
        """
        Get all blockchain blocks (paginated).
        
        Args:
            limit (int): Maximum number of blocks to return
            offset (int): Number of blocks to skip
            
        Returns:
            list: Blockchain blocks (most recent first)
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT id, previous_hash, current_hash, event_type, 
                           entity_type, entity_id, payload, created_at
                    FROM blockchain_logs
                    ORDER BY created_at DESC, id DESC
                    LIMIT %s OFFSET %s;
                """, (limit, offset))
                
                blocks = cursor.fetchall()
                
                return [{
                    'id': str(block[0]),
                    'previous_hash': block[1],
                    'current_hash': block[2],
                    'event_type': block[3],
                    'entity_type': block[4],
                    'entity_id': str(block[5]) if block[5] else None,
                    'payload': block[6],
                    'created_at': block[7].isoformat() if block[7] else None
                } for block in blocks]
                
        except Exception as e:
            logger.error(f"Failed to get all blocks: {e}")
            raise
    
    @staticmethod
    def get_blocks_by_event_type(event_type, limit=100):
        """
        Get blocks filtered by event type.
        
        Args:
            event_type (str): Event type to filter
            limit (int): Maximum blocks to return
            
        Returns:
            list: Blockchain blocks of specified event type
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT id, previous_hash, current_hash, event_type, 
                           entity_type, entity_id, payload, created_at
                    FROM blockchain_logs
                    WHERE event_type = %s
                    ORDER BY created_at DESC, id DESC
                    LIMIT %s;
                """, (event_type, limit))
                
                blocks = cursor.fetchall()
                
                return [{
                    'id': str(block[0]),
                    'previous_hash': block[1],
                    'current_hash': block[2],
                    'event_type': block[3],
                    'entity_type': block[4],
                    'entity_id': str(block[5]) if block[5] else None,
                    'payload': block[6],
                    'created_at': block[7].isoformat() if block[7] else None
                } for block in blocks]
                
        except Exception as e:
            logger.error(f"Failed to get blocks by event type {event_type}: {e}")
            raise
    
    @staticmethod
    def count_blocks():
        """
        Count total blocks in blockchain.
        
        Returns:
            int: Total number of blocks
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM blockchain_logs;")
                count = cursor.fetchone()[0]
                return count
                
        except Exception as e:
            logger.error(f"Failed to count blocks: {e}")
            raise
    
    @staticmethod
    def get_block_by_hash(current_hash):
        """
        Get block by its hash.
        
        Args:
            current_hash (str): SHA-256 hash of block
            
        Returns:
            dict: Block data
            None: If not found
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT id, previous_hash, current_hash, event_type, 
                           entity_type, entity_id, payload, created_at
                    FROM blockchain_logs
                    WHERE current_hash = %s;
                """, (current_hash,))
                
                block = cursor.fetchone()
                
                if not block:
                    return None
                
                return {
                    'id': str(block[0]),
                    'previous_hash': block[1],
                    'current_hash': block[2],
                    'event_type': block[3],
                    'entity_type': block[4],
                    'entity_id': str(block[5]) if block[5] else None,
                    'payload': block[6],
                    'created_at': block[7].isoformat() if block[7] else None
                }
                
        except Exception as e:
            logger.error(f"Failed to get block by hash: {e}")
            raise
    
    # =========================================================================
    # IMMUTABILITY ENFORCEMENT: NO UPDATE OR DELETE METHODS
    # =========================================================================
    # 
    # By design, this model does NOT provide:
    # - update() method
    # - delete() method
    # - Any method that modifies existing records
    #
    # This ensures blockchain immutability and tamper-evidence.
    # If a record needs correction, a new compensating block must be added.
    # =========================================================================
