"""
Exam Model
==========
Data access layer for exam-related database operations.

This module provides all database queries for exam management,
following the repository pattern.
"""

from models.database import get_db_cursor
from utils.logger import setup_logger
from datetime import datetime
import json

logger = setup_logger(__name__)


class Exam:
    """
    Exam model representing exam definitions and configurations.
    
    Provides methods for exam CRUD operations.
    """
    
    @staticmethod
    def create(title, description, created_by_admin, start_time, end_time, 
               duration_minutes, exam_config, status='draft'):
        """
        Create a new exam.
        
        Args:
            title (str): Exam title
            description (str): Exam description
            created_by_admin (str): Admin user UUID
            start_time (str): ISO format datetime
            end_time (str): ISO format datetime
            duration_minutes (int): Max duration per student
            exam_config (dict): Exam configuration (questions, settings)
            status (str): Initial status (default: 'draft')
            
        Returns:
            dict: Created exam data
            
        Raises:
            Exception: If exam creation fails
        """
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    INSERT INTO exams (
                        title, description, created_by_admin, 
                        start_time, end_time, duration_minutes, 
                        exam_config, status
                    )
                    VALUES (%s, %s, %s::uuid, %s, %s, %s, %s::jsonb, %s::exam_status)
                    RETURNING id, title, description, created_by_admin, 
                              start_time, end_time, duration_minutes, 
                              exam_config, status, created_at, updated_at;
                """, (title, description, created_by_admin, start_time, 
                      end_time, duration_minutes, json.dumps(exam_config), status))
                
                exam = cursor.fetchone()
                
                logger.info(f"Exam created: {title} (ID: {exam[0]})")
                
                return {
                    'id': str(exam[0]),
                    'title': exam[1],
                    'description': exam[2],
                    'created_by_admin': str(exam[3]),
                    'start_time': exam[4].isoformat() if exam[4] else None,
                    'end_time': exam[5].isoformat() if exam[5] else None,
                    'duration_minutes': exam[6],
                    'exam_config': exam[7],
                    'status': exam[8],
                    'created_at': exam[9].isoformat() if exam[9] else None,
                    'updated_at': exam[10].isoformat() if exam[10] else None
                }
                
        except Exception as e:
            logger.error(f"Failed to create exam: {e}")
            raise
    
    @staticmethod
    def find_by_id(exam_id):
        """
        Find exam by ID.
        
        Args:
            exam_id (str): Exam UUID
            
        Returns:
            dict: Exam data
            None: If exam not found
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT e.id, e.title, e.description, e.created_by_admin,
                           e.start_time, e.end_time, e.duration_minutes,
                           e.exam_config, e.status, e.created_at, e.updated_at,
                           u.full_name as admin_name, u.email as admin_email
                    FROM exams e
                    JOIN users u ON e.created_by_admin = u.id
                    WHERE e.id = %s::uuid;
                """, (exam_id,))
                
                exam = cursor.fetchone()
                
                if not exam:
                    return None
                
                return {
                    'id': str(exam[0]),
                    'title': exam[1],
                    'description': exam[2],
                    'created_by_admin': str(exam[3]),
                    'start_time': exam[4].isoformat() if exam[4] else None,
                    'end_time': exam[5].isoformat() if exam[5] else None,
                    'duration_minutes': exam[6],
                    'exam_config': exam[7],
                    'status': exam[8],
                    'created_at': exam[9].isoformat() if exam[9] else None,
                    'updated_at': exam[10].isoformat() if exam[10] else None,
                    'admin_name': exam[11],
                    'admin_email': exam[12]
                }
                
        except Exception as e:
            logger.error(f"Failed to find exam by ID {exam_id}: {e}")
            raise
    
    @staticmethod
    def update(exam_id, **kwargs):
        """
        Update exam fields.
        
        Args:
            exam_id (str): Exam UUID
            **kwargs: Fields to update (title, description, start_time, etc.)
            
        Returns:
            dict: Updated exam data
            None: If exam not found
        """
        try:
            # Build dynamic UPDATE query
            allowed_fields = ['title', 'description', 'start_time', 'end_time', 
                            'duration_minutes', 'exam_config', 'status']
            
            update_fields = []
            values = []
            
            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    if field == 'status':
                        update_fields.append(f"{field} = %s::exam_status")
                        values.append(value)
                    elif field == 'exam_config':
                        update_fields.append(f"{field} = %s::jsonb")
                        values.append(json.dumps(value))
                    else:
                        update_fields.append(f"{field} = %s")
                        values.append(value)
            
            if not update_fields:
                return Exam.find_by_id(exam_id)
            
            # Add exam_id to values
            values.append(exam_id)
            
            query = f"""
                UPDATE exams
                SET {', '.join(update_fields)}
                WHERE id = %s::uuid
                RETURNING id, title, description, created_by_admin,
                          start_time, end_time, duration_minutes,
                          exam_config, status, created_at, updated_at;
            """
            
            with get_db_cursor(commit=True) as cursor:
                cursor.execute(query, values)
                
                exam = cursor.fetchone()
                
                if not exam:
                    return None
                
                logger.info(f"Exam updated: {exam[0]}")
                
                return {
                    'id': str(exam[0]),
                    'title': exam[1],
                    'description': exam[2],
                    'created_by_admin': str(exam[3]),
                    'start_time': exam[4].isoformat() if exam[4] else None,
                    'end_time': exam[5].isoformat() if exam[5] else None,
                    'duration_minutes': exam[6],
                    'exam_config': exam[7],
                    'status': exam[8],
                    'created_at': exam[9].isoformat() if exam[9] else None,
                    'updated_at': exam[10].isoformat() if exam[10] else None
                }
                
        except Exception as e:
            logger.error(f"Failed to update exam {exam_id}: {e}")
            raise
    
    @staticmethod
    def delete(exam_id):
        """
        Delete exam (hard delete with CASCADE).
        
        Args:
            exam_id (str): Exam UUID
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    DELETE FROM exams
                    WHERE id = %s::uuid;
                """, (exam_id,))
                
                logger.info(f"Exam deleted: {exam_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete exam {exam_id}: {e}")
            raise
    
    @staticmethod
    def update_status(exam_id, status):
        """
        Update exam status.
        
        Args:
            exam_id (str): Exam UUID
            status (str): New status (draft, scheduled, active, completed, cancelled)
            
        Returns:
            dict: Updated exam data
        """
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    UPDATE exams
                    SET status = %s::exam_status
                    WHERE id = %s::uuid
                    RETURNING id, title, status;
                """, (status, exam_id))
                
                exam = cursor.fetchone()
                
                if not exam:
                    return None
                
                logger.info(f"Exam {exam[0]} status changed to: {status}")
                
                return {
                    'id': str(exam[0]),
                    'title': exam[1],
                    'status': exam[2]
                }
                
        except Exception as e:
            logger.error(f"Failed to update exam status {exam_id}: {e}")
            raise
    
    @staticmethod
    def get_all_exams(status=None, created_by=None):
        """
        Get all exams with optional filters.
        
        Args:
            status (str, optional): Filter by status
            created_by (str, optional): Filter by admin UUID
            
        Returns:
            list: List of exam dictionaries
        """
        try:
            conditions = []
            values = []
            
            if status:
                conditions.append("e.status = %s::exam_status")
                values.append(status)
            
            if created_by:
                conditions.append("e.created_by_admin = %s::uuid")
                values.append(created_by)
            
            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
            
            query = f"""
                SELECT e.id, e.title, e.description, e.created_by_admin,
                       e.start_time, e.end_time, e.duration_minutes,
                       e.status, e.created_at, u.full_name as admin_name
                FROM exams e
                JOIN users u ON e.created_by_admin = u.id
                {where_clause}
                ORDER BY e.created_at DESC;
            """
            
            with get_db_cursor() as cursor:
                cursor.execute(query, values if values else None)
                
                exams = cursor.fetchall()
                
                return [{
                    'id': str(exam[0]),
                    'title': exam[1],
                    'description': exam[2],
                    'created_by_admin': str(exam[3]),
                    'start_time': exam[4].isoformat() if exam[4] else None,
                    'end_time': exam[5].isoformat() if exam[5] else None,
                    'duration_minutes': exam[6],
                    'status': exam[7],
                    'created_at': exam[8].isoformat() if exam[8] else None,
                    'admin_name': exam[9]
                } for exam in exams]
                
        except Exception as e:
            logger.error(f"Failed to get exams: {e}")
            raise
    
    @staticmethod
    def get_available_exams():
        """
        Get exams available for students (scheduled or active status).
        
        Returns:
            list: List of available exam dictionaries (without exam_config)
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT e.id, e.title, e.description, e.start_time, 
                           e.end_time, e.duration_minutes, e.status,
                           u.full_name as admin_name
                    FROM exams e
                    JOIN users u ON e.created_by_admin = u.id
                    WHERE e.status IN ('scheduled'::exam_status, 'active'::exam_status)
                    ORDER BY e.start_time ASC;
                """)
                
                exams = cursor.fetchall()
                
                return [{
                    'id': str(exam[0]),
                    'title': exam[1],
                    'description': exam[2],
                    'start_time': exam[3].isoformat() if exam[3] else None,
                    'end_time': exam[4].isoformat() if exam[4] else None,
                    'duration_minutes': exam[5],
                    'status': exam[6],
                    'admin_name': exam[7]
                } for exam in exams]
                
        except Exception as e:
            logger.error(f"Failed to get available exams: {e}")
            raise
