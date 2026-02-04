from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class BlockchainBlock(Base):
    __tablename__ = "blockchain_ledger"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    index = Column(Integer, index=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Cryptographic Links
    previous_hash = Column(String, nullable=False)
    hash = Column(String, nullable=False, unique=True)
    
    # Data Payload
    event_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=True) # Linked User/Exam ID
    data = Column(JSON, nullable=False)
    
    # Verification
    signature = Column(String, nullable=True) # Digital signature of the authority
    validator_node = Column(String, default="NODE_01_PRIMARY")

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": str(self.timestamp),
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "data": self.data,
            "event_type": self.event_type
        }
