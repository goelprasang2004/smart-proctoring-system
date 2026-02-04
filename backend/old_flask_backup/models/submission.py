"""
Submission Model
================
Data access layer for exam submission operations.

Handles answer storage and scoring.
"""

from models.database import get_db_cursor
from utils.logger import setup_logger
import json

logger = setup_logger(__name__)


class Submission:
    """
    Submission model for exam answers and scores.
    """
    
    @staticmethod
    def create(attempt_id, answers, score=None, submission_metadata=None):
        """
        Create exam submission.
        
        Args:
            attempt_id (str): Attempt UUID
            answers (dict): Student answers
            score (float, optional): Calculated score
            submission_metadata (dict, optional): Additional metadata
            
        Returns:
            dict: Created submission
        """
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    INSERT INTO submissions (attempt_id, answers, score, submission_metadata)
                    VALUES (%s::uuid, %s::jsonb, %s, %s::jsonb)
                    RETURNING id, attempt_id, answers, score, submitted_at, submission_metadata;
                """, (attempt_id, json.dumps(answers), score, json.dumps(submission_metadata) if submission_metadata else None))
                
                row = cursor.fetchone()
                
                logger.info(f"Submission created for attempt {attempt_id}")
                
                return {
                    'id': str(row[0]),
                    'attempt_id': str(row[1]),
                    'answers': row[2],
                    'score': float(row[3]) if row[3] else None,
                    'submitted_at': row[4].isoformat() if row[4] else None,
                    'submission_metadata': row[5]
                }
                
        except Exception as e:
            logger.error(f"Failed to create submission: {e}")
            raise
    
    @staticmethod
    def find_by_attempt(attempt_id):
        """
        Get submission for an attempt.
        
        Args:
            attempt_id (str): Attempt UUID
            
        Returns:
            dict: Submission data
            None: If not found
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT s.id, s.attempt_id, s.answers, s.score, s.submitted_at,
                           s.submission_metadata,
                           e.title as exam_title, e.exam_config
                    FROM submissions s
                    JOIN exam_attempts ea ON s.attempt_id = ea.id
                    JOIN exams e ON ea.exam_id = e.id
                    WHERE s.attempt_id = %s::uuid;
                """, (attempt_id,))
                
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return {
                    'id': str(row[0]),
                    'attempt_id': str(row[1]),
                    'answers': row[2],
                    'score': float(row[3]) if row[3] else None,
                    'submitted_at': row[4].isoformat() if row[4] else None,
                    'submission_metadata': row[5],
                    'exam_title': row[6],
                    'exam_config': row[7]
                }
                
        except Exception as e:
            logger.error(f"Failed to find submission for attempt {attempt_id}: {e}")
            raise
    
    @staticmethod
    def find_by_student(student_id):
        """
        Get all submissions for a student.
        
        Args:
            student_id (str): Student UUID
            
        Returns:
            list: List of submissions with exam info
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT s.id, s.attempt_id, s.score, s.submitted_at,
                           e.title as exam_title, e.id as exam_id,
                           ea.started_at
                    FROM submissions s
                    JOIN exam_attempts ea ON s.attempt_id = ea.id
                    JOIN exams e ON ea.exam_id = e.id
                    WHERE ea.student_id = %s::uuid
                    ORDER BY s.submitted_at DESC;
                """, (student_id,))
                
                rows = cursor.fetchall()
                
                return [{
                    'id': str(row[0]),
                    'attempt_id': str(row[1]),
                    'score': float(row[2]) if row[2] else None,
                    'submitted_at': row[3].isoformat() if row[3] else None,
                    'exam_title': row[4],
                    'exam_id': str(row[5]),
                    'started_at': row[6].isoformat() if row[6] else None
                } for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get submissions for student {student_id}: {e}")
            raise
    
    @staticmethod
    def update_score(submission_id, score):
        """
        Update submission score.
        
        Args:
            submission_id (str): Submission UUID
            score (float): New score
            
        Returns:
            bool: Success
        """
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    UPDATE submissions
                    SET score = %s
                    WHERE id = %s::uuid;
                """, (score, submission_id))
                
                logger.info(f"Submission {submission_id} score updated to {score}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update submission score: {e}")
            raise
