"""
Exam Assignment Model
====================
Data access layer for exam assignment operations.

This module handles the relationship between exams and students,
tracking which exams are assigned to which students.
"""

from models.database import get_db_cursor
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ExamAssignment:
    """
    ExamAssignment model for managing exam-to-student assignments.
    
    Provides methods for creating, retrieving, and deleting assignments.
    """
    
    @staticmethod
    def create_assignment(exam_id, student_id, assigned_by_admin):
        """
        Assign an exam to a student.
        
        Args:
            exam_id (str): Exam UUID
            student_id (str): Student UUID
            assigned_by_admin (str): Admin UUID who created the assignment
            
        Returns:
            dict: Created assignment data
            
        Raises:
            Exception: If assignment already exists or creation fails
        """
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    INSERT INTO exam_assignments (exam_id, student_id, assigned_by_admin)
                    VALUES (%s, %s, %s)
                    RETURNING id, exam_id, student_id, assigned_at, assigned_by_admin
                """, (exam_id, student_id, assigned_by_admin))
                
                row = cursor.fetchone()
                
                if row:
                    return {
                        'id': str(row[0]),
                        'exam_id': str(row[1]),
                        'student_id': str(row[2]),
                        'assigned_at': row[3].isoformat() if row[3] else None,
                        'assigned_by_admin': str(row[4])
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Error creating exam assignment: {e}")
            raise
    
    @staticmethod
    def bulk_create_assignments(exam_id, student_ids, assigned_by_admin):
        """
        Assign an exam to multiple students at once.
        
        Args:
            exam_id (str): Exam UUID
            student_ids (list): List of student UUIDs
            assigned_by_admin (str): Admin UUID who created the assignments
            
        Returns:
            dict: {
                'success': list of created assignments,
                'failed': list of {student_id, error} for failures
            }
        """
        success = []
        failed = []
        
        for student_id in student_ids:
            try:
                assignment = ExamAssignment.create_assignment(
                    exam_id, student_id, assigned_by_admin
                )
                success.append(assignment)
            except Exception as e:
                error_msg = str(e)
                # Check if it's a duplicate key error
                if 'unique_exam_student_assignment' in error_msg or 'duplicate' in error_msg.lower():
                    failed.append({
                        'student_id': student_id,
                        'error': 'Already assigned'
                    })
                else:
                    failed.append({
                        'student_id': student_id,
                        'error': error_msg
                    })
        
        return {
            'success': success,
            'failed': failed
        }
    
    @staticmethod
    def get_assignments_for_exam(exam_id):
        """
        Get all students assigned to a specific exam.
        
        Args:
            exam_id (str): Exam UUID
            
        Returns:
            list: List of assignment dictionaries with student details
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        ea.id,
                        ea.exam_id,
                        ea.student_id,
                        ea.assigned_at,
                        ea.assigned_by_admin,
                        u.email,
                        u.full_name
                    FROM exam_assignments ea
                    JOIN users u ON ea.student_id = u.id
                    WHERE ea.exam_id = %s
                    ORDER BY ea.assigned_at DESC
                """, (exam_id,))
                
                rows = cursor.fetchall()
                
                assignments = []
                for row in rows:
                    assignments.append({
                        'id': str(row[0]),
                        'exam_id': str(row[1]),
                        'student_id': str(row[2]),
                        'assigned_at': row[3].isoformat() if row[3] else None,
                        'assigned_by_admin': str(row[4]),
                        'student_email': row[5],
                        'student_name': row[6]
                    })
                
                return assignments
                
        except Exception as e:
            logger.error(f"Error fetching assignments for exam {exam_id}: {e}")
            raise
    
    @staticmethod
    def get_assignments_for_student(student_id):
        """
        Get all exams assigned to a specific student.
        
        Args:
            student_id (str): Student UUID
            
        Returns:
            list: List of assigned exam dictionaries
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        ea.id,
                        ea.exam_id,
                        ea.student_id,
                        ea.assigned_at,
                        e.title,
                        e.description,
                        e.start_time,
                        e.end_time,
                        e.duration_minutes,
                        e.status
                    FROM exam_assignments ea
                    JOIN exams e ON ea.exam_id = e.id
                    WHERE ea.student_id = %s
                    ORDER BY e.start_time ASC
                """, (student_id,))
                
                rows = cursor.fetchall()
                
                exams = []
                for row in rows:
                    exams.append({
                        'assignment_id': str(row[0]),
                        'exam_id': str(row[1]),
                        'student_id': str(row[2]),
                        'assigned_at': row[3].isoformat() if row[3] else None,
                        'title': row[4],
                        'description': row[5],
                        'start_time': row[6].isoformat() if row[6] else None,
                        'end_time': row[7].isoformat() if row[7] else None,
                        'duration_minutes': row[8],
                        'status': row[9]
                    })
                
                return exams
                
        except Exception as e:
            logger.error(f"Error fetching assignments for student {student_id}: {e}")
            raise
    
    @staticmethod
    def remove_assignment(exam_id, student_id):
        """
        Remove an exam assignment from a student.
        
        Args:
            exam_id (str): Exam UUID
            student_id (str): Student UUID
            
        Returns:
            bool: True if deleted, False if not found
        """
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    DELETE FROM exam_assignments
                    WHERE exam_id = %s AND student_id = %s
                    RETURNING id
                """, (exam_id, student_id))
                
                result = cursor.fetchone()
                return result is not None
                
        except Exception as e:
            logger.error(f"Error removing assignment: {e}")
            raise
    
    @staticmethod
    def check_if_assigned(exam_id, student_id):
        """
        Check if a student is assigned to an exam.
        
        Args:
            exam_id (str): Exam UUID
            student_id (str): Student UUID
            
        Returns:
            bool: True if assigned, False otherwise
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM exam_assignments
                        WHERE exam_id = %s AND student_id = %s
                    )
                """, (exam_id, student_id))
                
                result = cursor.fetchone()
                return result[0] if result else False
                
        except Exception as e:
            logger.error(f"Error checking assignment: {e}")
            return False
    
    @staticmethod
    def get_assigned_student_count(exam_id):
        """
        Get the count of students assigned to an exam.
        
        Args:
            exam_id (str): Exam UUID
            
        Returns:
            int: Number of students assigned
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM exam_assignments
                    WHERE exam_id = %s
                """, (exam_id,))
                
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except Exception as e:
            logger.error(f"Error counting assignments: {e}")
            return 0
