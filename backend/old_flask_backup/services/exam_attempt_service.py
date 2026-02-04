"""
Exam Attempt Service
===================
Business logic for exam attempt management.

Handles exam session creation, submission, and scoring.
"""

from models.exam_attempt import ExamAttempt
from models.submission import Submission
from models.exam import Exam
from models.exam_assignment import ExamAssignment
from services.exam_session_security import ExamSessionSecurity
from utils.logger import setup_logger
from datetime import datetime

logger = setup_logger(__name__)


class ExamAttemptService:
    """
    Service for managing exam attempts and submissions.
    """
    
    @staticmethod
    def start_attempt(exam_id, student_id, session_data=None):
        """
        Start a new exam attempt with security checks.
        
        Args:
            exam_id (str): Exam UUID
            student_id (str): Student UUID
            session_data (dict, optional): Session metadata
            
        Returns:
            dict: Created attempt with exam config
            
        Raises:
            ValueError: If validation fails
        """
        # Check for existing active attempt
        ExamSessionSecurity.enforce_single_session(student_id, exam_id)
        
        # Get exam details
        exam = Exam.find_by_id(exam_id)
        if not exam:
            raise ValueError("Exam not found")
        
        # Verify exam is available (scheduled, active, or draft for testing)
        if exam['status'] not in ['draft', 'scheduled', 'active', 'in_progress']:
            raise ValueError(f"Exam is not available. Current status: {exam['status']}")
        
        # Verify student is assigned to this exam
        if not ExamAssignment.check_if_assigned(exam_id, student_id):
            logger.warning(f"Student {student_id} attempted to access unassigned exam {exam_id}")
            raise ValueError("You are not assigned to this exam. Please contact your administrator.")
        
        # Verify exam time window (commented for testing - enable in production)
        # now = datetime.now()
        # start_time = datetime.fromisoformat(exam['start_time'].replace('Z', '+00:00'))
        # end_time = datetime.fromisoformat(exam['end_time'].replace('Z', '+00:00'))
        # 
        # if now < start_time:
        #     raise ValueError("Exam has not started yet")
        # 
        # if now > end_time:
        #     raise ValueError("Exam has ended")
        
        # Create attempt
        attempt = ExamAttempt.create(exam_id, student_id, session_data)
        
        # Add exam config to response
        attempt['exam_config'] = exam['exam_config']
        attempt['exam_title'] = exam['title']
        attempt['duration_minutes'] = exam['duration_minutes']
        
        logger.info(f"Exam attempt started: student={student_id}, exam={exam_id}")
        return attempt
    
    @staticmethod
    def submit_attempt(attempt_id, student_id, answers):
        """
        Submit exam attempt with answers.
        
        Args:
            attempt_id (str): Attempt UUID
            student_id (str): Student UUID (for verification)
            answers (dict): Student answers
            
        Returns:
            dict: Submission with score
            
        Raises:
            ValueError: If validation fails
        """
        # Get attempt
        attempt = ExamAttempt.find_by_id(attempt_id)
        if not attempt:
            raise ValueError("Attempt not found")
        
        # Verify ownership
        if attempt['student_id'] != student_id:
            raise ValueError("Attempt does not belong to student")
        
        # Verify attempt is active
        if attempt['status'] != 'in_progress':
            raise ValueError(f"Attempt is {attempt['status']}, cannot submit")
        
        # Calculate score
        score = ExamAttemptService._calculate_score(answers, attempt['exam_config'])
        
        # Create submission
        submission = Submission.create(
            attempt_id=attempt_id,
            answers=answers,
            score=score,
            submission_metadata={
                'submitted_at': datetime.now().isoformat(),
                'total_questions': len(attempt['exam_config'].get('questions', []))
            }
        )
        
        # Update attempt status
        ExamAttempt.update_status(attempt_id, 'completed', datetime.now())
        
        logger.info(f"Exam submitted: attempt={attempt_id}, score={score}")
        
        return submission
    
    @staticmethod
    def _calculate_score(answers, exam_config):
        """
        Calculate exam score based on answers.
        
        Args:
            answers (dict): Student answers {question_id: answer}
           exam_config (dict): Exam configuration with questions
            
        Returns:
            float: Score (0-100)
        """
        questions = exam_config.get('questions', [])
        if not questions:
            return 0.0
        
        total_points = 0
        earned_points = 0
        
        for question in questions:
            q_id = str(question.get('id'))
            points = question.get('points', 1)
            correct_answer = question.get('correct_answer')
            
            total_points += points
            
            # Check if student answered correctly
            student_answer = answers.get(q_id)
            if student_answer and student_answer == correct_answer:
                earned_points += points
        
        # Calculate percentage
        if total_points == 0:
            return 0.0
        
        return round((earned_points / total_points) * 100, 2)
    
    @staticmethod
    def get_student_attempts(student_id):
        """
        Get all attempts for a student.
        
        Args:
            student_id (str): Student UUID
            
        Returns:
            list: List of attempts with scores
        """
        return ExamAttempt.find_by_student(student_id)
    
    @staticmethod
    def get_attempt_details(attempt_id, student_id=None):
        """
        Get attempt details.
        
        Args:
            attempt_id (str): Attempt UUID
            student_id (str, optional): For ownership verification
            
        Returns:
            dict: Attempt details
            
        Raises:
            ValueError: If not found or unauthorized
        """
        attempt = ExamAttempt.find_by_id(attempt_id)
        
        if not attempt:
            raise ValueError("Attempt not found")
        
        # Verify ownership if student_id provided
        if student_id and attempt['student_id'] != student_id:
            raise ValueError("Attempt does not belong to student")
        
        return attempt
    
    @staticmethod
    def terminate_attempt(attempt_id, student_id, reason, event_type):
        """
        Terminate exam attempt due to proctoring violation.
        
        Args:
            attempt_id (str): Attempt UUID
            student_id (str): Student UUID (for verification)
            reason (str): Termination reason
            event_type (str): Type of violation event
            
        Returns:
            dict: Termination result
            
        Raises:
            ValueError: If validation fails
        """
        from models.proctoring import ProctoringEvent
        
        # Get attempt
        attempt = ExamAttempt.find_by_id(attempt_id)
        if not attempt:
            raise ValueError("Attempt not found")
        
        # Verify ownership
        if attempt['student_id'] != student_id:
            raise ValueError("Attempt does not belong to student")
        
        # Verify attempt is active
        if attempt['status'] != 'in_progress':
            raise ValueError(f"Attempt is already {attempt['status']}, cannot terminate")
        
        # Log termination event
        ProctoringEvent.create(
            attempt_id=attempt_id,
            event_type='exam_terminated',
            description=f"Exam auto-terminated: {reason}",
            ai_response={
                'termination_reason': reason,
                'trigger_event': event_type,
                'terminated_at': datetime.now().isoformat()
            },
            confidence_score=1.0
        )
        
        # Update attempt status to terminated
        ExamAttempt.update_status(attempt_id, 'terminated', datetime.now())
        
        logger.warning(f"Exam terminated: attempt={attempt_id}, reason={reason}, event_type={event_type}")
        
        return {
            'attempt_id': attempt_id,
            'status': 'terminated',
            'reason': reason,
            'event_type': event_type
        }

