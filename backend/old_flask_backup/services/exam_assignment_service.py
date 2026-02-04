"""
Exam Assignment Service
=======================
Business logic for exam assignment operations.

Handles:
- Assignment validation
- Student and exam verification
- Bulk assignment processing
- Permission checks
"""

from models.exam_assignment import ExamAssignment
from models.exam import Exam
from models.user import User
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ExamAssignmentService:
    """
    Service layer for exam assignment business logic.
    
    Validates assignments and enforces business rules.
    """
    
    @staticmethod
    def assign_exam_to_students(exam_id, student_ids, assigned_by_admin):
        """
        Assign an exam to one or more students with validation.
        
        Args:
            exam_id (str): Exam UUID
            student_ids (list): List of student UUIDs
            assigned_by_admin (str): Admin UUID
            
        Returns:
            dict: {
                'success': list of created assignments,
                'failed': list of failures with reasons
            }
            
        Raises:
            ValueError: If exam doesn't exist or is not assignable
        """
        # Validate exam exists
        exam = Exam.find_by_id(exam_id)
        if not exam:
            raise ValueError("Exam not found")
        
        # Validate exam status (don't assign cancelled exams)
        if exam['status'] == 'cancelled':
            raise ValueError(f"Cannot assign cancelled exam. Exam has been cancelled and is no longer available for assignment.")
        
        # Validate admin exists
        admin = User.find_by_id(assigned_by_admin)
        if not admin:
            raise ValueError("Admin not found")
        
        # Validate each student and filter valid ones
        valid_student_ids = []
        failed = []
        
        for student_id in student_ids:
            student = User.find_by_id(student_id)
            
            if not student:
                failed.append({
                    'student_id': student_id,
                    'error': 'Student not found'
                })
                continue
            
            # Check if user is actually a student
            if student.get('role') != 'student':
                failed.append({
                    'student_id': student_id,
                    'error': f"User is not a student (role: {student.get('role')})"
                })
                continue
            
            valid_student_ids.append(student_id)
        
        # Bulk create assignments for valid students
        if valid_student_ids:
            result = ExamAssignment.bulk_create_assignments(
                exam_id, valid_student_ids, assigned_by_admin
            )
            
            # Merge the failed lists
            failed.extend(result['failed'])
            
            logger.info(
                f"Admin {assigned_by_admin} assigned exam {exam_id} to {len(result['success'])} students. "
                f"{len(failed)} failed."
            )
            
            return {
                'success': result['success'],
                'failed': failed
            }
        else:
            logger.warning(f"No valid students to assign for exam {exam_id}")
            return {
                'success': [],
                'failed': failed
            }
    
    @staticmethod
    def remove_assignment(exam_id, student_id):
        """
        Remove an exam assignment with validation.
        
        Args:
            exam_id (str): Exam UUID
            student_id (str): Student UUID
            
        Returns:
            bool: True if removed
            
        Raises:
            ValueError: If exam or student not found, or assignment doesn't exist
        """
        # Validate exam exists
        exam = Exam.find_by_id(exam_id)
        if not exam:
            raise ValueError("Exam not found")
        
        # Validate student exists
        student = User.find_by_id(student_id)
        if not student:
            raise ValueError("Student not found")
        
        # Check if assignment exists
        if not ExamAssignment.check_if_assigned(exam_id, student_id):
            raise ValueError("Assignment does not exist")
        
        # Remove assignment
        result = ExamAssignment.remove_assignment(exam_id, student_id)
        
        logger.info(f"Removed assignment: exam {exam_id} from student {student_id}")
        return result
    
    @staticmethod
    def get_exam_assignments(exam_id):
        """
        Get all students assigned to an exam.
        
        Args:
            exam_id (str): Exam UUID
            
        Returns:
            list: List of assignment dictionaries
            
        Raises:
            ValueError: If exam not found
        """
        # Validate exam exists
        exam = Exam.find_by_id(exam_id)
        if not exam:
            raise ValueError("Exam not found")
        
        return ExamAssignment.get_assignments_for_exam(exam_id)
    
    @staticmethod
    def get_student_assigned_exams(student_id):
        """
        Get all exams assigned to a student.
        
        Args:
            student_id (str): Student UUID
            
        Returns:
            list: List of assigned exam dictionaries
            
        Raises:
            ValueError: If student not found
        """
        # Validate student exists
        student = User.find_by_id(student_id)
        if not student:
            raise ValueError("Student not found")
        
        if student.get('role') != 'student':
            raise ValueError("User is not a student")
        
        return ExamAssignment.get_assignments_for_student(student_id)
    
    @staticmethod
    def get_available_exams_for_student(student_id):
        """
        Get available exams for a specific student (assigned + scheduled/active).
        Includes attempt status for each exam.
        
        Args:
            student_id (str): Student UUID
            
        Returns:
            list: List of available exam dictionaries (without exam_config)
        """
        try:
            from services.exam_session_security import ExamSessionSecurity
            
            # Get all assigned exams for this student
            assigned_exams = ExamAssignment.get_assignments_for_student(student_id)
            
            # Filter to only show scheduled or active exams
            available_exams = []
            for exam in assigned_exams:
                if exam['status'] in ['scheduled', 'active']:
                    # Remove exam_config if present (students shouldn't see questions before attempt)
                    exam_copy = exam.copy()
                    exam_copy.pop('exam_config', None)
                    # Frontend expects 'id', so map exam_id to id
                    exam_copy['id'] = exam_copy['exam_id']
                    
                    # Check if student has completed or in-progress attempt
                    completed_attempt = ExamSessionSecurity.check_completed_attempt(
                        student_id, exam_copy['exam_id']
                    )
                    active_attempt = ExamSessionSecurity.check_active_attempt(
                        student_id, exam_copy['exam_id']
                    )
                    
                    if completed_attempt:
                        exam_copy['attempt_status'] = completed_attempt['status']
                        exam_copy['attempt_id'] = completed_attempt['id']
                        exam_copy['can_start'] = False
                    elif active_attempt:
                        exam_copy['attempt_status'] = 'in_progress'
                        exam_copy['attempt_id'] = active_attempt['id']
                        exam_copy['can_start'] = False  # Already started
                    else:
                        exam_copy['attempt_status'] = None
                        exam_copy['attempt_id'] = None
                        exam_copy['can_start'] = True
                    
                    available_exams.append(exam_copy)
            
            return available_exams
            
        except Exception as e:
            logger.error(f"Error getting available exams for student {student_id}: {e}")
            raise

