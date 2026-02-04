import hashlib
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.blockchain import BlockchainBlock
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import ECC
from Cryptodome.Signature import DSS

class BlockchainService:
    def __init__(self, db: Session):
        self.db = db
        # specific private key for signing (in production this comes from HSM/Vault)
        # generating a temp key for this session if not loaded
        self.private_key = ECC.generate(curve='P-256')
        self.signer = DSS.new(self.private_key, 'fips-186-3')

    def _calculate_hash(self, index, previous_hash, timestamp, data):
        """
        SHA-256 hash of block content
        """
        block_string = json.dumps({
            "index": index,
            "previous_hash": previous_hash,
            "timestamp": str(timestamp),
            "data": data
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def _sign_block(self, block_hash):
        """
        Sign the block hash with ECDSA
        """
        h = SHA256.new(block_hash.encode('utf-8'))
        signature = self.signer.sign(h)
        return signature.hex()

    def get_latest_block(self):
        return self.db.query(BlockchainBlock).order_by(BlockchainBlock.index.desc()).first()

    def create_block(self, event_type: str, data: dict, entity_id: str = None):
        """
        Create a new immutable block linked to the previous one
        """
        latest_block = self.get_latest_block()
        
        new_index = 1
        previous_hash = "0" * 64 # Genesis hash
        
        if latest_block:
            new_index = latest_block.index + 1
            previous_hash = latest_block.hash
            
        timestamp = datetime.utcnow()
        
        # Calculate Hash
        current_hash = self._calculate_hash(new_index, previous_hash, timestamp, data)
        
        # Sign Hash
        signature = self._sign_block(current_hash)
        
        # Create Block Record
        new_block = BlockchainBlock(
            index=new_index,
            timestamp=timestamp,
            previous_hash=previous_hash,
            hash=current_hash,
            event_type=event_type,
            entity_id=entity_id,
            data=data,
            signature=signature
        )
        
        self.db.add(new_block)
        self.db.commit()
        self.db.refresh(new_block)
        return new_block

    def verify_chain(self):
        """
        Verify the integrity of the entire ledger
        """
        blocks = self.db.query(BlockchainBlock).order_by(BlockchainBlock.index.asc()).all()
        
        for i in range(1, len(blocks)):
            current = blocks[i]
            previous = blocks[i-1]
            
            # 1. Check Link
            if current.previous_hash != previous.hash:
                return False, f"Broken link at block {current.index}"
                
            # 2. Check Hash Integrity
            recalulated_hash = self._calculate_hash(
                current.index, 
                current.previous_hash, 
                current.timestamp, 
                current.data
            )
            
            if current.hash != recalulated_hash:
                return False, f"Data modification detected at block {current.index}"
                
        return True, "Chain is valid"
