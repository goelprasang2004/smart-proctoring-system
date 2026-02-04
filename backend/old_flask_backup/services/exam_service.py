"""
Exam Service
============
Business logic for exam management.

Handles:
- Exam creation and validation
- Status transition logic
- Time validation
- Role-based access rules
"""

from models.exam import Exam
from utils.logger import setup_logger
from datetime import datetime

logger = setup_logger(__name__)


class ExamService:
    """
    Exam service handling all exam-related business logic.
    """
    
    # Valid status transitions
    VALID_TRANSITIONS = {
        'draft': ['scheduled', 'cancelled'],
        'scheduled': ['active', 'cancelled'],
        'active': ['completed', 'cancelled'],
        'completed': [],  # Terminal state
        'cancelled': []   # Terminal state
    }
    
    @staticmethod
    def create_exam(title, description, created_by_admin, start_time, end_time,
                    duration_minutes, exam_config):
        """
        Create a new exam with validation.
        
        Args:
            title (str): Exam title
            description (str): Exam description (optional)
            created_by_admin (str): Admin user UUID
            start_time (str): ISO format datetime
            end_time (str): ISO format datetime
            duration_minutes (int): Max duration per student
            exam_config (dict): Exam configuration
            
        Returns:
            dict: Created exam data
            
        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        if not title or not title.strip():
            raise ValueError("Exam title is required")
        
        if not start_time or not end_time:
            raise ValueError("Start time and end time are required")
        
        if not duration_minutes or duration_minutes <= 0:
            raise ValueError("Duration must be greater than 0")
        
        if not exam_config or not isinstance(exam_config, dict):
            raise ValueError("Exam config must be a valid object")
        
        # Validate time range
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            if end_dt <= start_dt:
                raise ValueError("End time must be after start time")
                
        except ValueError as e:
            if "End time must be after start time" in str(e):
                raise
            raise ValueError("Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
        
        # Create exam with default 'draft' status
        exam = Exam.create(
            title=title,
            description=description,
            created_by_admin=created_by_admin,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration_minutes,
            exam_config=exam_config,
            status='draft'
        )
        
        logger.info(f"Exam created by admin {created_by_admin}: {exam['id']}")
        return exam
    
    @staticmethod
    def update_exam(exam_id, **kwargs):
        """
        Update exam with validation.
        
        Args:
            exam_id (str): Exam UUID
            **kwargs: Fields to update
            
        Returns:
            dict: Updated exam data
            
        Raises:
            ValueError: If validation fails
        """
        # Get current exam
        current_exam = Exam.find_by_id(exam_id)
        
        if not current_exam:
            raise ValueError("Exam not found")
        
        # Validate time range if both provided
        if 'start_time' in kwargs or 'end_time' in kwargs:
            start_time = kwargs.get('start_time', current_exam['start_time'])
            end_time = kwargs.get('end_time', current_exam['end_time'])
            
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                
                if end_dt <= start_dt:
                    raise ValueError("End time must be after start time")
                    
            except ValueError as e:
                if "End time must be after start time" in str(e):
                    raise
                raise ValueError("Invalid datetime format")
        
        # Validate duration if provided
        if 'duration_minutes' in kwargs:
            if kwargs['duration_minutes'] <= 0:
                raise ValueError("Duration must be greater than 0")
        
        # Update exam
        updated_exam = Exam.update(exam_id, **kwargs)
        
        logger.info(f"Exam updated: {exam_id}")
        return updated_exam
    
    @staticmethod
    def delete_exam(exam_id):
        """
        Delete exam.
        
        Args:
            exam_id (str): Exam UUID
            
        Returns:
            bool: True if deleted
            
        Raises:
            ValueError: If exam not found
        """
        # Verify exam exists
        exam = Exam.find_by_id(exam_id)
        
        if not exam:
            raise ValueError("Exam not found")
        
        # Delete exam
        Exam.delete(exam_id)
        
        logger.info(f"Exam deleted: {exam_id}")
        return True
    
    @staticmethod
    def change_status(exam_id, new_status):
        """
        Change exam status with validation.
        
        Args:
            exam_id (str): Exam UUID
            new_status (str): New status
            
        Returns:
            dict: Updated exam data
            
        Raises:
            ValueError: If transition is invalid
        """
        # Get current exam
        exam = Exam.find_by_id(exam_id)
        
        if not exam:
            raise ValueError("Exam not found")
        
        current_status = exam['status']
        
        # Validate status transition
        valid_next_statuses = ExamService.VALID_TRANSITIONS.get(current_status, [])
        
        if new_status not in valid_next_statuses:
            raise ValueError(
                f"Invalid status transition: {current_status} -> {new_status}. "
                f"Valid transitions from {current_status}: {', '.join(valid_next_statuses) if valid_next_statuses else 'none (terminal state)'}"
            )
        
        # Update status
        updated_exam = Exam.update_status(exam_id, new_status)
        
        logger.info(f"Exam {exam_id} status changed: {current_status} -> {new_status}")
        return updated_exam
    
    @staticmethod
    def get_exam_details(exam_id, include_config=False):
        """
        Get exam details.
        
        Args:
            exam_id (str): Exam UUID
            include_config (bool): Whether to include exam_config (admin only)
            
        Returns:
            dict: Exam data
        """
        exam = Exam.find_by_id(exam_id)
        
        if not exam:
            raise ValueError("Exam not found")
        
        # Remove exam_config if not requested (student view)
        if not include_config and 'exam_config' in exam:
            exam = exam.copy()
            exam.pop('exam_config', None)
        
        return exam
    
    @staticmethod
    def get_all_exams_for_admin(status=None, created_by=None):
        """
        Get all exams for admin view.
        
        Args:
            status (str, optional): Filter by status
            created_by (str, optional): Filter by admin
            
        Returns:
            list: List of exams
        """
        return Exam.get_all_exams(status=status, created_by=created_by)
    
    @staticmethod
    def get_available_exams_for_student():
        """
        Get exams available for students (scheduled or active only).
        
        Returns:
            list: List of available exams (without questions)
        """
        return Exam.get_available_exams()
