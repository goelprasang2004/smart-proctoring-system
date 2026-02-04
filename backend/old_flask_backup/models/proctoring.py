"""
Proctoring Event Model
======================
Data access layer for proctoring event logging.

This module provides database operations for proctoring_logs table,
tracking student behavior during exam attempts.
"""

from models.database import get_db_cursor
from utils.logger import setup_logger
from datetime import datetime
import json

logger = setup_logger(__name__)


class ProctoringEvent:
    """
    Proctoring event model for logging student behavior during exams.
    
    Tracks events like:
    - face_detection
    - voice_detection
    - stress_alert
    - tab_switch
    - window_blur
    - multiple_faces
    - no_face
    - suspicious_behavior
    """
    
    @staticmethod
    def create(attempt_id, event_type, description, confidence_score=None, metadata=None):
        """
        Log a proctoring event.
        
        Args:
            attempt_id (str): Exam attempt UUID
            event_type (str): Type of event (from proctoring_event ENUM)
            description (str): Human-readable event description
            confidence_score (float, optional): AI confidence score (0.0 to 1.0)
            metadata (dict, optional): Additional event data (JSONB)
            
        Returns:
            dict: Created proctoring event
            
        Raises:
            Exception: If event creation fails
        """
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    INSERT INTO proctoring_logs (
                        attempt_id, event_type, description, 
                        confidence_score, metadata
                    )
                    VALUES (
                        %s::uuid, %s::proctoring_event, %s, %s, %s::jsonb
                    )
                    RETURNING id, attempt_id, timestamp, event_type, 
                              description, confidence_score, metadata;
                """, (attempt_id, event_type, description, confidence_score, json.dumps(metadata) if metadata else None))
                
                event = cursor.fetchone()
                
                logger.info(f"Proctoring event logged: {event_type} for attempt {attempt_id}")
                
                return {
                    'id': str(event[0]),
                    'attempt_id': str(event[1]),
                    'timestamp': event[2].isoformat() if event[2] else None,
                    'event_type': event[3],
                    'description': event[4],
                    'confidence_score': float(event[5]) if event[5] else None,
                    'metadata': event[6]
                }
                
        except Exception as e:
            logger.error(f"Failed to create proctoring event: {e}")
            raise
    
    @staticmethod
    def get_by_attempt(attempt_id, event_type=None, limit=None):
        """
        Get all proctoring events for an exam attempt.
        
        Args:
            attempt_id (str): Exam attempt UUID
            event_type (str, optional): Filter by specific event type
            limit (int, optional): Limit number of results
            
        Returns:
            list: List of proctoring events
        """
        try:
            conditions = ["attempt_id = %s::uuid"]
            values = [attempt_id]
            
            if event_type:
                conditions.append("event_type = %s::proctoring_event")
                values.append(event_type)
            
            where_clause = " AND ".join(conditions)
            limit_clause = f"LIMIT {limit}" if limit else ""
            
            query = f"""
                SELECT id, attempt_id, timestamp, event_type, 
                       description, confidence_score, metadata
                FROM proctoring_logs
                WHERE {where_clause}
                ORDER BY timestamp DESC
                {limit_clause};
            """
            
            with get_db_cursor() as cursor:
                cursor.execute(query, values)
                
                events = cursor.fetchall()
                
                return [{
                    'id': str(event[0]),
                    'attempt_id': str(event[1]),
                    'timestamp': event[2].isoformat() if event[2] else None,
                    'event_type': event[3],
                    'description': event[4],
                    'confidence_score': float(event[5]) if event[5] else None,
                    'metadata': event[6]
                } for event in events]
                
        except Exception as e:
            logger.error(f"Failed to get proctoring events for attempt {attempt_id}: {e}")
            raise
    
    @staticmethod
    def get_suspicious_events(attempt_id, confidence_threshold=0.7):
        """
        Get suspicious events (high confidence of anomaly).
        
        Args:
            attempt_id (str): Exam attempt UUID
            confidence_threshold (float): Minimum confidence to be considered suspicious
            
        Returns:
            list: List of suspicious events
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT id, attempt_id, timestamp, event_type, 
                           description, confidence_score, metadata
                    FROM proctoring_logs
                    WHERE attempt_id = %s::uuid
                    AND confidence_score >= %s
                    ORDER BY confidence_score DESC, timestamp DESC;
                """, (attempt_id, confidence_threshold))
                
                events = cursor.fetchall()
                
                return [{
                    'id': str(event[0]),
                    'attempt_id': str(event[1]),
                    'timestamp': event[2].isoformat() if event[2] else None,
                    'event_type': event[3],
                    'description': event[4],
                    'confidence_score': float(event[5]) if event[5] else None,
                    'metadata': event[6]
                } for event in events]
                
        except Exception as e:
            logger.error(f"Failed to get suspicious events for attempt {attempt_id}: {e}")
            raise
    
    @staticmethod
    def count_by_type(attempt_id, event_type):
        """
        Count occurrences of specific event type for an attempt.
        
        Args:
            attempt_id (str): Exam attempt UUID
            event_type (str): Event type to count
            
        Returns:
            int: Number of occurrences
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM proctoring_logs
                    WHERE attempt_id = %s::uuid
                    AND event_type = %s::proctoring_event;
                """, (attempt_id, event_type))
                
                count = cursor.fetchone()[0]
                return count
                
        except Exception as e:
            logger.error(f"Failed to count events for attempt {attempt_id}: {e}")
            raise
    
    @staticmethod
    def get_event_summary(attempt_id):
        """
        Get event count summary for an attempt.
        
        Args:
            attempt_id (str): Exam attempt UUID
            
        Returns:
            dict: Event counts by type
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT event_type, COUNT(*) as count,
                           AVG(confidence_score) as avg_confidence
                    FROM proctoring_logs
                    WHERE attempt_id = %s::uuid
                    GROUP BY event_type
                    ORDER BY count DESC;
                """, (attempt_id,))
                
                summary = cursor.fetchall()
                
                return [{
                    'event_type': row[0],
                    'count': row[1],
                    'avg_confidence': float(row[2]) if row[2] else None
                } for row in summary]
                
        except Exception as e:
            logger.error(f"Failed to get event summary for attempt {attempt_id}: {e}")
            raise
    
    @staticmethod
    def get_all_suspicious_attempts(confidence_threshold=0.7, min_event_count=5):
        """
        Get all exam attempts with suspicious activity.
        
        Args:
            confidence_threshold (float): Minimum confidence score
            min_event_count (int): Minimum number of suspicious events
            
        Returns:
            list: List of suspicious attempts with event counts
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        pl.attempt_id,
                        ea.exam_id,
                        ea.student_id,
                        u.email as student_email,
                        u.full_name as student_name,
                        COUNT(pl.id) as suspicious_event_count,
                        AVG(pl.confidence_score) as avg_confidence,
                        ea.status as attempt_status,
                        STRING_AGG(DISTINCT pl.event_type::text, ', ' ORDER BY pl.event_type::text) as event_types
                    FROM proctoring_logs pl
                    JOIN exam_attempts ea ON pl.attempt_id = ea.id
                    JOIN users u ON ea.student_id = u.id
                    WHERE pl.confidence_score >= %s
                    GROUP BY pl.attempt_id, ea.exam_id, ea.student_id, 
                             u.email, u.full_name, ea.status
                    HAVING COUNT(pl.id) >= %s
                    ORDER BY COUNT(pl.id) DESC, AVG(pl.confidence_score) DESC;
                """, (confidence_threshold, min_event_count))
                
                attempts = cursor.fetchall()
                
                return [{
                    'attempt_id': str(row[0]),
                    'exam_id': str(row[1]),
                    'student_id': str(row[2]),
                    'student_email': row[3],
                    'student_name': row[4],
                    'suspicious_event_count': row[5],
                    'avg_confidence': float(row[6]) if row[6] else None,
                    'status': row[7],
                    'event_types': row[8].split(', ') if row[8] else []
                } for row in attempts]
                
        except Exception as e:
            logger.error(f"Failed to get suspicious attempts: {e}")
            raise
    
    @staticmethod
    def delete_by_attempt(attempt_id):
        """
        Delete all proctoring events for an attempt.
        
        Args:
            attempt_id (str): Exam attempt UUID
            
        Returns:
            int: Number of events deleted
        """
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    DELETE FROM proctoring_logs
                    WHERE attempt_id = %s::uuid;
                """, (attempt_id,))
                
                deleted_count = cursor.rowcount
                logger.info(f"Deleted {deleted_count} proctoring events for attempt {attempt_id}")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to delete proctoring events for attempt {attempt_id}: {e}")
            raise
