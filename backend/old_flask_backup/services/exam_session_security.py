"""
Exam Session Security Service
==============================
Prevents concurrent exam attempts and session hijacking.

Handles:
- Session validation
- Concurrent attempt prevention
- Device/IP binding
- Auto-termination on suspicious activity
"""

from models.database import get_db_cursor
from utils.logger import setup_logger, log_security_event
from datetime import datetime

logger = setup_logger(__name__)


class ExamSessionSecurity:
    """
    Exam session security enforcement.
    
    Prevents:
    - Multiple concurrent attempts
    - Session hijacking
    - Unauthorized access
    """
    
    @staticmethod
    def check_active_attempt(student_id, exam_id):
        """
        Check if student already has an active attempt for this exam.
        
        Active = status IN ('in_progress')
        
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
                    SELECT id, student_id, exam_id, status, started_at, 
                           submitted_at, session_data
                    FROM exam_attempts
                    WHERE student_id = %s::uuid
                    AND exam_id = %s::uuid
                    AND status = 'in_progress'
                    LIMIT 1;
                """, (student_id, exam_id))
                
                attempt = cursor.fetchone()
                
                if not attempt:
                    return None
                
                return {
                    'id': str(attempt[0]),
                    'student_id': str(attempt[1]),
                    'exam_id': str(attempt[2]),
                    'status': attempt[3],
                    'started_at': attempt[4].isoformat() if attempt[4] else None,
                    'submitted_at': attempt[5].isoformat() if attempt[5] else None,
                    'session_data': attempt[6]
                }
                
        except Exception as e:
            logger.error(f"Failed to check active attempt: {e}")
            raise
    
    @staticmethod
    def validate_session(attempt_id, student_id, ip_address=None, user_agent=None):
        """
        Validate exam session integrity.
        
        Checks:
        - Attempt exists and belongs to student
        - Attempt is still in progress
        - IP/User-Agent matches original (if strict mode)
        
        Args:
            attempt_id (str): Exam attempt UUID
            student_id (str): Student UUID
            ip_address (str, optional): Current IP address
            user_agent (str, optional): Current user agent
            
        Returns:
            dict: Validation result
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT id, student_id, exam_id, status, session_data
                    FROM exam_attempts
                    WHERE id = %s::uuid;
                """, (attempt_id,))
                
                attempt = cursor.fetchone()
                
                if not attempt:
                    log_security_event(
                        logger,
                        event_type='exam_attempt_not_found',
                        details={'attempt_id': attempt_id, 'user_id': student_id}
                    )
                    return {
                        'valid': False,
                        'reason': 'Attempt not found'
                    }
                
                # Check ownership
                if str(attempt[1]) != str(student_id):
                    log_security_event(
                        logger,
                        event_type='exam_attempt_ownership_violation',
                        details={
                            'attempt_id': attempt_id,
                            'actual_student': str(attempt[1]),
                            'user_id': student_id
                        }
                    )
                    return {
                        'valid': False,
                        'reason': 'Attempt does not belong to student'
                    }
                
                # Check status
                if attempt[3] != 'in_progress':
                    return {
                        'valid': False,
                        'reason': f'Attempt is {attempt[3]}, not in progress'
                    }
                
                # Optional: Check IP/User-Agent for session hijacking
                session_data = attempt[4] or {}
                
                if ip_address and session_data.get('ip_address'):
                    if ip_address != session_data.get('ip_address'):
                        log_security_event(
                            logger,
                            event_type='exam_session_ip_mismatch',
                            details={
                                'attempt_id': attempt_id,
                                'original_ip': session_data.get('ip_address'),
                                'current_ip': ip_address,
                                'user_id': student_id
                            }
                        )
                        # WARNING logged but not blocking (mobile networks change IPs)
                
                return {
                    'valid': True,
                    'attempt_id': str(attempt[0]),
                    'exam_id': str(attempt[2]),
                    'status': attempt[3]
                }
                
        except Exception as e:
            logger.error(f"Session validation failed: {e}")
            raise
    
    @staticmethod
    def terminate_suspicious_session(attempt_id, reason, terminated_by_user_id=None):
        """
        Terminate exam session due to suspicious activity.
        
        Args:
            attempt_id (str): Exam attempt UUID
            reason (str): Reason for termination
            terminated_by_user_id (str, optional): Admin who terminated
            
        Returns:
            bool: Success
        """
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    UPDATE exam_attempts
                    SET status = 'terminated',
                        submitted_at = CURRENT_TIMESTAMP
                    WHERE id = %s::uuid
                    AND status = 'in_progress';
                """, (attempt_id,))
                
                if cursor.rowcount == 0:
                    logger.warning(f"No active attempt found to terminate: {attempt_id}")
                    return False
                
                log_security_event(
                    logger,
                    event_type='exam_session_terminated',
                    details={
                        'attempt_id': attempt_id,
                        'reason': reason,
                        'terminated_by': terminated_by_user_id
                    }
                )
                
                logger.info(f"Exam session terminated: {attempt_id} - {reason}")
                
                # Log to blockchain
                try:
                    from services.blockchain_service import BlockchainService, BlockchainEvents, BlockchainEntities
                    BlockchainService.log_event(
                        event_type=BlockchainEvents.EXAM_ATTEMPT_TERMINATE,
                        entity_type=BlockchainEntities.EXAM_ATTEMPT,
                        entity_id=attempt_id,
                        payload={
                            'reason': reason,
                            'terminated_by': terminated_by_user_id
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to log termination to blockchain: {e}")
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to terminate session: {e}")
            raise
    
    @staticmethod
    def auto_terminate_on_violation(attempt_id, violation_type, violation_data):
        """
        Auto-terminate session based on proctoring violations.
        
        Violation types:
        - high_risk_ai_analysis (anomaly >= 0.9)
        - multiple_suspicious_events (count >= threshold)
        - manual_admin_termination
        
        Args:
            attempt_id (str): Exam attempt UUID
            violation_type (str): Type of violation
            violation_data (dict): Violation details
            
        Returns:
            bool: Whether termination occurred
        """
        # Define termination thresholds
        AUTO_TERMINATE_RULES = {
            'high_risk_ai_analysis': {
                'threshold': 0.9,
                'field': 'anomaly_score'
            },
            'suspicious_event_count': {
                'threshold': 10,
                'field': 'count'
            }
        }
        
        should_terminate = False
        reason = None
        
        if violation_type in AUTO_TERMINATE_RULES:
            rule = AUTO_TERMINATE_RULES[violation_type]
            value = violation_data.get(rule['field'], 0)
            
            if value >= rule['threshold']:
                should_terminate = True
                reason = f"Auto-terminated: {violation_type} exceeded threshold ({value} >= {rule['threshold']})"
        
        if should_terminate:
            logger.warning(f"Auto-terminating attempt {attempt_id}: {reason}")
            return ExamSessionSecurity.terminate_suspicious_session(
                attempt_id=attempt_id,
                reason=reason,
                terminated_by_user_id=None  # System-initiated
            )
        
        return False
    
    @staticmethod
    def get_concurrent_attempt_count(student_id):
        """
        Get count of student's concurrent exam attempts.
        
        Args:
            student_id (str): Student UUID
            
        Returns:
            int: Number of in-progress attempts
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM exam_attempts
                    WHERE student_id = %s::uuid
                    AND status = 'in_progress';
                """, (student_id,))
                
                count = cursor.fetchone()[0]
                return count
                
        except Exception as e:
            logger.error(f"Failed to count concurrent attempts: {e}")
            raise
    
    @staticmethod
    def check_completed_attempt(student_id, exam_id):
        """
        Check if student has already completed this exam.
        
        Completed = status IN ('completed', 'submitted', 'terminated')
        
        Args:
            student_id (str): Student UUID
            exam_id (str): Exam UUID
            
        Returns:
            dict: Completed attempt if exists
            None: If no completed attempt
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT id, student_id, exam_id, status, started_at, 
                           submitted_at
                    FROM exam_attempts
                    WHERE student_id = %s::uuid
                    AND exam_id = %s::uuid
                    AND status IN ('completed', 'terminated', 'cancelled')
                    ORDER BY submitted_at DESC
                    LIMIT 1;
                """, (student_id, exam_id))
                
                attempt = cursor.fetchone()
                
                if not attempt:
                    return None
                
                return {
                    'id': str(attempt[0]),
                    'student_id': str(attempt[1]),
                    'exam_id': str(attempt[2]),
                    'status': attempt[3],
                    'started_at': attempt[4].isoformat() if attempt[4] else None,
                    'submitted_at': attempt[5].isoformat() if attempt[5] else None
                }
                
        except Exception as e:
            logger.error(f"Failed to check completed attempt: {e}")
            raise
    
    @staticmethod
    def enforce_single_session(student_id, exam_id):
        """
        Enforce single active session per student per exam.
        Also prevents restart of completed exams.
        
        Args:
            student_id (str): Student UUID
            exam_id (str): Exam UUID
            
        Returns:
            dict: Enforcement result
            
        Raises:
            ValueError: If active or completed attempt already exists
        """
        # First check if exam is already completed
        completed_attempt = ExamSessionSecurity.check_completed_attempt(student_id, exam_id)
        
        if completed_attempt:
            log_security_event(
                logger,
                event_type='completed_exam_restart_blocked',
                details={
                    'exam_id': exam_id,
                    'completed_attempt_id': completed_attempt['id'],
                    'completed_status': completed_attempt['status'],
                    'user_id': student_id
                }
            )
            
            raise ValueError(
                f"You have already completed this exam. "
                f"Status: {completed_attempt['status']}. "
                f"You cannot retake this exam."
            )
        
        # Then check for active in-progress attempt
        active_attempt = ExamSessionSecurity.check_active_attempt(student_id, exam_id)
        
        if active_attempt:
            log_security_event(
                logger,
                event_type='concurrent_attempt_blocked',
                details={
                    'exam_id': exam_id,
                    'existing_attempt_id': active_attempt['id'],
                    'user_id': student_id
                }
            )
            
            raise ValueError(
                f"You already have an active attempt for this exam. "
                f"Please complete or terminate attempt {active_attempt['id']} first."
            )
        
        return {'allowed': True}
