"""
Blockchain Hash Utility
========================
Cryptographic hash generation for blockchain audit trail.

Uses SHA-256 for deterministic, tamper-evident hashing.
No external blockchain libraries required.
"""

import hashlib
import json
from datetime import datetime


class BlockchainHasher:
    """
    Handles SHA-256 hash generation for blockchain blocks.
    
    Provides deterministic hashing for:
    - Block content
    - Chain linking
    - Tamper detection
    """
    
    @staticmethod
    def generate_block_hash(previous_hash, event_type, entity_type, 
                           entity_id, payload, timestamp=None):
        """
        Generate SHA-256 hash for a blockchain block.
        
        Hash input includes:
        - previous_hash (links to previous block)
        - event_type (what happened)
        - entity_type (what entity)
        - entity_id (which specific instance)
        - payload (event data)
        - timestamp (when it happened)
        
        Args:
            previous_hash (str): Hash of previous block (None for genesis)
            event_type (str): Type of event
            entity_type (str): Type of entity
            entity_id (str): UUID of entity (can be None)
            payload (dict): Event payload data
            timestamp (str, optional): ISO timestamp (uses current if None)
            
        Returns:
            str: 64-character hexadecimal SHA-256 hash
        """
        # Use current timestamp if not provided
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        
        # Build canonical block data structure
        block_data = {
            'previous_hash': previous_hash if previous_hash else 'GENESIS',
            'event_type': event_type,
            'entity_type': entity_type,
            'entity_id': str(entity_id) if entity_id else 'NULL',
            'payload': payload if payload else {},
            'timestamp': timestamp
        }
        
        # Convert to deterministic JSON string
        # sort_keys ensures same data always produces same hash
        block_string = json.dumps(block_data, sort_keys=True, separators=(',', ':'))
        
        # Generate SHA-256 hash
        hash_object = hashlib.sha256(block_string.encode('utf-8'))
        current_hash = hash_object.hexdigest()
        
        return current_hash
    
    @staticmethod
    def verify_block_hash(block):
        """
        Verify that a block's stored hash matches recomputed hash.
        
        Args:
            block (dict): Block data with current_hash
            
        Returns:
            bool: True if hash is valid, False if tampered
        """
        stored_hash = block.get('current_hash')
        
        if not stored_hash:
            return False
        
        # Recompute hash from block data
        recomputed_hash = BlockchainHasher.generate_block_hash(
            previous_hash=block.get('previous_hash'),
            event_type=block.get('event_type'),
            entity_type=block.get('entity_type'),
            entity_id=block.get('entity_id'),
            payload=block.get('payload'),
            timestamp=block.get('created_at')
        )
        
        # Compare stored vs recomputed
        return stored_hash == recomputed_hash
    
    @staticmethod
    def verify_chain_integrity(blocks):
        """
        Verify integrity of entire blockchain chain.
        
        Checks:
        1. Each block's hash is valid (not tampered)
        2. Each block's previous_hash matches previous block's current_hash
        
        Args:
            blocks (list): List of blocks in chronological order
            
        Returns:
            dict: Verification result with details
        """
        if not blocks:
            return {
                'valid': True,
                'message': 'Empty chain',
                'total_blocks': 0,
                'verified_blocks': 0
            }
        
        verified_count = 0
        broken_links = []
        tampered_blocks = []
        
        for i, block in enumerate(blocks):
            # Check 1: Verify block hash
            if not BlockchainHasher.verify_block_hash(block):
                tampered_blocks.append({
                    'index': i,
                    'block_id': block.get('id'),
                    'reason': 'Hash mismatch - block tampered'
                })
                continue
            
            # Check 2: Verify chain link (except genesis block)
            if i > 0:
                previous_block = blocks[i - 1]
                expected_previous_hash = previous_block.get('current_hash')
                actual_previous_hash = block.get('previous_hash')
                
                if expected_previous_hash != actual_previous_hash:
                    broken_links.append({
                        'index': i,
                        'block_id': block.get('id'),
                        'expected': expected_previous_hash,
                        'actual': actual_previous_hash
                    })
                    continue
            
            verified_count += 1
        
        is_valid = (verified_count == len(blocks))
        
        return {
            'valid': is_valid,
            'message': 'Chain valid' if is_valid else 'Chain compromised',
            'total_blocks': len(blocks),
            'verified_blocks': verified_count,
            'tampered_blocks': tampered_blocks,
            'broken_links': broken_links
        }
    
    @staticmethod
    def create_genesis_block_hash(system_name='Smart Proctoring System'):
        """
        Create hash for genesis block (first block in chain).
        
        Genesis block has no previous_hash.
        
        Args:
            system_name (str): Name of system (for genesis identification)
            
        Returns:
            str: SHA-256 hash for genesis block
        """
        genesis_data = {
            'previous_hash': 'GENESIS',
            'event_type': 'system_init',
            'entity_type': 'system',
            'entity_id': 'NULL',
            'payload': {
                'system': system_name,
                'version': '1.0',
                'description': 'Blockchain audit trail initialized'
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        genesis_string = json.dumps(genesis_data, sort_keys=True, separators=(',', ':'))
        hash_object = hashlib.sha256(genesis_string.encode('utf-8'))
        
        return hash_object.hexdigest()
    
    @staticmethod
    def hash_data(data):
        """
        General-purpose SHA-256 hash for any data.
        
        Args:
            data (str or dict): Data to hash
            
        Returns:
            str: SHA-256 hash
        """
        if isinstance(data, dict):
            data_string = json.dumps(data, sort_keys=True, separators=(',', ':'))
        else:
            data_string = str(data)
        
        hash_object = hashlib.sha256(data_string.encode('utf-8'))
        return hash_object.hexdigest()
