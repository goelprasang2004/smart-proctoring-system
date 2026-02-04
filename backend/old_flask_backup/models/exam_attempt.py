"""
Exam Attempt Model
==================
Database model for exam attempts with session tracking.
"""

import json
from models.database import get_db_cursor
from utils.logger import setup_logger
import uuid

logger = setup_logger(__name__)


class ExamAttempt:
    """
    Exam Attempt model for managing student exam sessions.
    """
    
    @staticmethod
    def create(exam_id, student_id, session_data=None):
        """
        Create a new exam attempt.
        
        Args:
            exam_id (str): Exam UUID
            student_id (str): Student UUID
            session_data (dict, optional): Session metadata (IP, user agent, etc.)
            
        Returns:
            dict: Created attempt data
        """
        try:
            with get_db_cursor(commit=True) as cursor:
                # Convert session_data dict to JSON string for PostgreSQL
                session_json = json.dumps(session_data) if session_data else None
                
                cursor.execute("""
                    INSERT INTO exam_attempts (exam_id, student_id, browser_metadata, status)
                    VALUES (%s::uuid, %s::uuid, %s::jsonb, 'in_progress'::attempt_status)
                    RETURNING id, exam_id, student_id, started_at, submitted_at, 
                              status, browser_metadata, created_at;
                """, (exam_id, student_id, session_json))
                
                attempt = cursor.fetchone()
                
                logger.info(f"Exam attempt created: {attempt[0]}")
                
                return {
                    'id': str(attempt[0]),
                    'exam_id': str(attempt[1]),
                    'student_id': str(attempt[2]),
                    'started_at': attempt[3].isoformat() if attempt[3] else None,
                    'submitted_at': attempt[4].isoformat() if attempt[4] else None,
                    'status': attempt[5],
                    'browser_metadata': attempt[6],
                    'created_at': attempt[7].isoformat() if attempt[7] else None
                }
                
        except Exception as e:
            logger.error(f"Failed to create exam attempt: {e}")
            raise
    
    @staticmethod
    def find_by_id(attempt_id):
        """
        Find attempt by ID.
        
        Args:
            attempt_id (str): Attempt UUID
            
        Returns:
            dict: Attempt data with exam config
            None: If not found
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT ea.id, ea.exam_id, ea.student_id, ea.started_at,
                           ea.submitted_at, ea.status, ea.session_data,
                           e.title, e.duration_minutes, e.exam_config,
                           e.start_time, e.end_time
                    FROM exam_attempts ea
                    JOIN exams e ON ea.exam_id = e.id
                    WHERE ea.id = %s::uuid;
                """, (attempt_id,))
                
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return {
                    'id': str(row[0]),
                    'exam_id': str(row[1]),
                    'student_id': str(row[2]),
                    'started_at': row[3].isoformat() if row[3] else None,
                    'submitted_at': row[4].isoformat() if row[4] else None,
                    'status': row[5],
                    'session_data': row[6],
                    'exam_title': row[7],
                    'duration_minutes': row[8],
                    'exam_config': row[9],
                    'exam_start_time': row[10].isoformat() if row[10] else None,
                    'exam_end_time': row[11].isoformat() if row[11] else None
                }
                
        except Exception as e:
            logger.error(f"Failed to find attempt {attempt_id}: {e}")
            raise
    
    @staticmethod
    def find_by_student(student_id):
        """
        Get all attempts for a student.
        
        Args:
            student_id (str): Student UUID
            
        Returns:
            list: List of attempts
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT ea.id, ea.exam_id, ea.started_at, ea.submitted_at,
                           ea.status, e.title, s.score
                    FROM exam_attempts ea
                    JOIN exams e ON ea.exam_id = e.id
                    LEFT JOIN submissions s ON ea.id = s.attempt_id
                    WHERE ea.student_id = %s::uuid
                    ORDER BY ea.started_at DESC;
                """, (student_id,))
                
                rows = cursor.fetchall()
                
                return [{ 
                    'id': str(row[0]),
                    'exam_id': str(row[1]),
                    'started_at': row[2].isoformat() if row[2] else None,
                    'submitted_at': row[3].isoformat() if row[3] else None,
                    'status': row[4],
                    'exam_title': row[5],
                    'score': float(row[6]) if row[6] else None
                } for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get attempts for student {student_id}: {e}")
            raise
    
    @staticmethod
    def update_status(attempt_id, status, submitted_at=None):
        """
        Update attempt status.
        
        Args:
            attempt_id (str): Attempt UUID
            status (str): New status
            submitted_at (datetime, optional): Submission time
            
        Returns:
            bool: Success
        """
        try:
            with get_db_cursor(commit=True) as cursor:
                if submitted_at:
                    cursor.execute("""
                        UPDATE exam_attempts
                        SET status = %s::attempt_status, submitted_at = %s
                        WHERE id = %s::uuid;
                    """, (status, submitted_at, attempt_id))
                else:
                    cursor.execute("""
                        UPDATE exam_attempts
                        SET status = %s::attempt_status
                        WHERE id = %s::uuid;
                    """, (status, attempt_id))
                
                logger.info(f"Attempt {attempt_id} status updated to {status}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update attempt status: {e}")
            raise
    
    @staticmethod
    def check_active_attempt(student_id, exam_id):
        """
        Check if student has an active attempt for this exam.
        
        Args:
            student_id (str): Student UUID
            exam_id (str): Exam UUID
            
        Returns:
            dict: Active attempt if exists
            None: If no active attempt
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT id, exam_id, student_id, started_at, status
                    FROM exam_attempts
                    WHERE student_id = %s::uuid
                    AND exam_id = %s::uuid
                    AND status = 'in_progress'::attempt_status
                    LIMIT 1;
                """, (student_id, exam_id))
                
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return {
                    'id': str(row[0]),
                    'exam_id': str(row[1]),
                    'student_id': str(row[2]),
                    'started_at': row[3].isoformat() if row[3] else None,
                    'status': row[4]
                }
                
        except Exception as e:
            logger.error(f"Failed to check active attempt: {e}")
            raise
