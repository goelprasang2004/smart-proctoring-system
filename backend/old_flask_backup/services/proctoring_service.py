"""
Proctoring Service
==================
Business logic for proctoring event processing and AI analysis.

Handles:
- Event validation and logging
- AI confidence simulation (ready for real AI integration)
- Anomaly detection
- Risk assessment
"""

from models.proctoring import ProctoringEvent
from models.ai_analysis import AIAnalysis
from utils.logger import setup_logger
import random
import json

logger = setup_logger(__name__)


class ProctoringService:
    """
    Proctoring service handling event processing and AI simulation.
    """
    
    # Event severity mapping (for risk calculation)
    EVENT_SEVERITY = {
        'face_detection': 0.2,      # Low severity (normal operation)
        'voice_detection': 0.2,     # Low severity
        'stress_alert': 0.6,        # Medium-high severity
        'tab_switch': 0.5,          # Medium severity
        'window_blur': 0.4,         # Medium-low severity
        'multiple_faces': 0.9,      # High severity
        'no_face': 0.8,             # High severity
        'suspicious_behavior': 0.7  # Medium-high severity
    }
    
    @staticmethod
    def log_event(attempt_id, event_type, description, metadata=None):
        """
        Log a proctoring event with simulated AI confidence.
        
        Args:
            attempt_id (str): Exam attempt UUID
            event_type (str): Type of event
            description (str): Event description
            metadata (dict, optional): Additional event data
            
        Returns:
            dict: Logged event with confidence score
            
        Raises:
            ValueError: If validation fails
        """
        # Validate event type
        if event_type not in ProctoringService.EVENT_SEVERITY:
            raise ValueError(f"Invalid event type: {event_type}")
        
        # Simulate AI confidence score
        # In production, this would call real AI service
        confidence_score = ProctoringService._simulate_confidence(event_type, metadata)
        
        # Log event
        event = ProctoringEvent.create(
            attempt_id=attempt_id,
            event_type=event_type,
            description=description,
            confidence_score=confidence_score,
            metadata=metadata
        )
        
        # Trigger AI analysis if confidence is high
        if confidence_score >= 0.7:
            ProctoringService._trigger_ai_analysis(attempt_id, event_type, metadata, confidence_score)
            
            # Log suspicious event to blockchain
            try:
                from services.blockchain_service import BlockchainService, BlockchainEvents, BlockchainEntities
                BlockchainService.log_event(
                    event_type=BlockchainEvents.PROCTORING_SUSPICIOUS,
                    entity_type=BlockchainEntities.PROCTORING_LOG,
                    entity_id=attempt_id,
                    payload={
                        'proctoring_event_type': event_type,
                        'confidence_score': confidence_score,
                        'description': description
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to log blockchain event: {e}")
        
        logger.info(f"Proctoring event logged: {event_type} (confidence: {confidence_score:.2f})")
        
        return event
    
    @staticmethod
    def _simulate_confidence(event_type, metadata=None):
        """
        Simulate AI confidence score.
        
        In production, replace with actual AI model:
        - Face recognition: OpenCV + DeepFace
        - Voice: speech recognition API
        - Stress: sentiment analysis
        
        Args:
            event_type (str): Type of event
            metadata (dict): Event metadata
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        base_severity = ProctoringService.EVENT_SEVERITY.get(event_type, 0.5)
        
        # Add randomness to simulate AI uncertainty (±0.15)
        # In production, this would be actual AI confidence
        noise = random.uniform(-0.15, 0.15)
        # Clamp to valid range BEFORE any further adjustments
        confidence = max(0.0, min(1.0, base_severity + noise))
        
        # Adjust based on metadata if available
        if metadata:
            # Example: Multiple occurrences increase confidence
            if 'occurrence_count' in metadata and metadata['occurrence_count'] > 3:
                # Clamp after each adjustment to ensure bounds
                confidence = max(0.0, min(1.0, confidence + 0.1))
        
        # Final bounds check to ensure 4 decimal places within [0, 1]
        confidence = max(0.0, min(1.0, confidence))
        return round(confidence, 4)
    
    @staticmethod
    def _trigger_ai_analysis(attempt_id, event_type, metadata, confidence_score):
        """
        Trigger AI analysis for high-confidence events.
        
        Args:
            attempt_id (str): Exam attempt UUID
            event_type (str): Event type
            metadata (dict): Event data
            confidence_score (float): Event confidence
        """
        # Map event type to analysis type
        analysis_type_mapping = {
            'face_detection': 'face_recognition',
            'multiple_faces': 'face_recognition',
            'no_face': 'face_recognition',
            'voice_detection': 'voice_recognition',
            'stress_alert': 'stress_detection',
            'tab_switch': 'behavioral_analysis',
            'window_blur': 'behavioral_analysis',
            'suspicious_behavior': 'behavioral_analysis'
        }
        
        analysis_type = analysis_type_mapping.get(event_type, 'behavioral_analysis')
        
        # Simulate AI analysis result
        result_data = ProctoringService._simulate_ai_result(analysis_type, event_type, metadata)
        
        # Calculate anomaly score
        anomaly_score = ProctoringService._calculate_anomaly_score(confidence_score, result_data)
        
        # Generate recommendations
        recommendations = ProctoringService._generate_recommendations(
            analysis_type, anomaly_score, result_data
        )
        
        # Store AI analysis
        AIAnalysis.create(
            attempt_id=attempt_id,
            analysis_type=analysis_type,
            result_data=result_data,
            anomaly_score=anomaly_score,
            recommendations=recommendations
        )
        
        logger.info(f"AI analysis triggered: {analysis_type} (anomaly: {anomaly_score:.2f})")
        
        # Log high-risk AI analysis to blockchain
        if anomaly_score >= 0.7:
            try:
                from services.blockchain_service import BlockchainService, BlockchainEvents, BlockchainEntities
                BlockchainService.log_event(
                    event_type=BlockchainEvents.AI_ANALYSIS_HIGH_RISK,
                    entity_type=BlockchainEntities.AI_ANALYSIS,
                    entity_id=attempt_id,
                    payload={
                        'analysis_type': analysis_type,
                        'anomaly_score': anomaly_score,
                        'recommendations': recommendations
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to log blockchain event for AI analysis: {e}")
    
    @staticmethod
    def _simulate_ai_result(analysis_type, event_type, metadata):
        """
        Simulate AI analysis result.
        
        In production, replace with actual AI service calls:
        - Face recognition: DeepFace.verify()
        - Voice: SpeechRecognition API
        - Stress: Sentiment analysis
        - Behavior: Pattern analysis
        
        Args:
            analysis_type (str): Type of AI analysis
            event_type (str): Original event type
            metadata (dict): Event metadata
            
        Returns:
            dict: Simulated AI result
        """
        if analysis_type == 'face_recognition':
            return {
                'faces_detected': 1 if event_type == 'face_detection' else 0 if event_type == 'no_face' else 2,
                'match_confidence': random.uniform(0.7, 0.98) if event_type == 'face_detection' else random.uniform(0.3, 0.6),
                'face_position': {'x': random.randint(100, 500), 'y': random.randint(50, 300)},
                'simulation': True
            }
        elif analysis_type == 'voice_recognition':
            return {
                'voice_detected': True,
                'speaker_count': random.randint(1, 2),
                'background_noise_level': random.uniform(0.2, 0.8),
                'simulation': True
            }
        elif analysis_type == 'stress_detection':
            return {
                'stress_level': random.uniform(0.5, 0.9),
                'heart_rate_estimated': random.randint(80, 120),
                'facial_tension_score': random.uniform(0.4, 0.8),
                'simulation': True
            }
        else:  # behavioral_analysis
            return {
                'behavior_type': event_type,
                'frequency': metadata.get('occurrence_count', 1) if metadata else 1,
                'pattern_detected': random.choice([True, False]),
                'simulation': True
            }
    
    @staticmethod
    def _calculate_anomaly_score(confidence_score, result_data):
        """
        Calculate anomaly score from AI result.
        
        Args:
            confidence_score (float): Event confidence
            result_data (dict): AI result data
            
        Returns:
            float: Anomaly score (0.0 to 1.0)
        """
        # Base anomaly on confidence
        anomaly = confidence_score * 0.7
        
        # Adjust based on result data
        if 'faces_detected' in result_data:
            if result_data['faces_detected'] == 0:
                anomaly = min(1.0, anomaly + 0.2)
            elif result_data['faces_detected'] > 1:
                anomaly = min(1.0, anomaly + 0.3)
        
        if 'stress_level' in result_data:
            anomaly = min(1.0, anomaly + result_data['stress_level'] * 0.2)
        
        if 'frequency' in result_data and result_data['frequency'] > 5:
            anomaly = min(1.0, anomaly + 0.15)
        
        return round(anomaly, 4)
    
    @staticmethod
    def _generate_recommendations(analysis_type, anomaly_score, result_data):
        """
        Generate recommendations based on AI analysis.
        
        Args:
            analysis_type (str): Type of analysis
            anomaly_score (float): Anomaly score
            result_data (dict): AI result
            
        Returns:
            str: Recommendations
        """
        if anomaly_score < 0.3:
            return "No significant anomalies detected. Student behavior appears normal."
        elif anomaly_score < 0.6:
            return f"Moderate anomaly detected in {analysis_type}. Review recommended."
        else:
            return f"High anomaly detected in {analysis_type}. Manual review required. Flag for investigation."
    
    @staticmethod
    def get_attempt_events(attempt_id, event_type=None):
        """
        Get proctoring events for an attempt.
        
        Args:
            attempt_id (str): Exam attempt UUID
            event_type (str, optional): Filter by event type
            
        Returns:
            list: Proctoring events
        """
        return ProctoringEvent.get_by_attempt(attempt_id, event_type=event_type)
    
    @staticmethod
    def get_attempt_ai_analysis(attempt_id, analysis_type=None):
        """
        Get AI analyses for an attempt.
        
        Args:
            attempt_id (str): Exam attempt UUID
            analysis_type (str, optional): Filter by analysis type
            
        Returns:
            list: AI analyses
        """
        return AIAnalysis.get_by_attempt(attempt_id, analysis_type=analysis_type)
    
    @staticmethod
    def get_suspicious_events(attempt_id, confidence_threshold=0.7):
        """
        Get suspicious events for an attempt.
        
        Args:
            attempt_id (str): Exam attempt UUID
            confidence_threshold (float): Minimum confidence
            
        Returns:
            list: Suspicious events
        """
        return ProctoringEvent.get_suspicious_events(attempt_id, confidence_threshold)
    
    @staticmethod
    def get_proctoring_summary(attempt_id):
        """
        Get comprehensive proctoring summary for an attempt.
        
        Args:
            attempt_id (str): Exam attempt UUID
            
        Returns:
            dict: Summary with events, AI analysis, and risk score
            
        Raises:
            ValueError: If attempt not found
        """
        try:
            # Get event summary (may be empty list)
            event_summary = ProctoringEvent.get_event_summary(attempt_id)
            if not event_summary:
                event_summary = []
            
            # Get AI analysis summary (handles None and empty dict)
            ai_summary = AIAnalysis.get_summary_by_attempt(attempt_id)
            if not ai_summary:
                ai_summary = {
                    'total_analyses': 0,
                    'avg_anomaly_score': None,
                    'max_anomaly_score': None,
                    'min_anomaly_score': None
                }
            
            # Get suspicious events count (may be empty list)
            suspicious_events = ProctoringEvent.get_suspicious_events(attempt_id, confidence_threshold=0.7)
            if not suspicious_events:
                suspicious_events = []
            
            # Calculate overall risk score
            risk_score = ProctoringService._calculate_risk_score(event_summary, ai_summary, suspicious_events)
            
            return {
                'attempt_id': attempt_id,
                'event_summary': event_summary,
                'ai_summary': ai_summary,
                'suspicious_event_count': len(suspicious_events),
                'risk_score': risk_score,
                'risk_level': ProctoringService._get_risk_level(risk_score)
            }
        except Exception as e:
            logger.error(f"Error getting proctoring summary for attempt {attempt_id}: {e}")
            raise ValueError(f"Failed to retrieve proctoring summary: {str(e)}")
    
    @staticmethod
    def _calculate_risk_score(event_summary, ai_summary, suspicious_events):
        """
        Calculate overall risk score for an attempt.
        
        Args:
            event_summary (list): Event counts by type (or None)
            ai_summary (dict): AI analysis summary (or None)
            suspicious_events (list): High-confidence events
            
        Returns:
            float: Risk score (0.0 to 1.0)
        """
        risk = 0.0
        
        # Factor 1: Suspicious event count (0-0.4)
        suspicious_count = len(suspicious_events) if suspicious_events else 0
        risk += min(0.4, suspicious_count * 0.05)
        
        # Factor 2: Average anomaly score (0-0.3)
        # Handle None, empty dict, or missing key
        if ai_summary and isinstance(ai_summary, dict) and ai_summary.get('avg_anomaly_score'):
            avg_anomaly = float(ai_summary['avg_anomaly_score'])
            risk += min(0.3, avg_anomaly * 0.3)
        
        # Factor 3: High-severity events (0-0.3)
        high_severity_count = 0
        if event_summary and isinstance(event_summary, list):
            high_severity_count = sum(
                summary.get('count', 0) for summary in event_summary
                if summary.get('event_type') in ['multiple_faces', 'no_face', 'suspicious_behavior']
            )
        risk += min(0.3, high_severity_count * 0.1)
        
        # Final clamp to ensure result is within [0, 1]
        return round(max(0.0, min(1.0, risk)), 4)
    
    @staticmethod
    def _get_risk_level(risk_score):
        """
        Convert risk score to categorical level.
        
        Args:
            risk_score (float): Risk score
            
        Returns:
            str: Risk level (LOW, MEDIUM, HIGH)
        """
        if risk_score < 0.3:
            return 'LOW'
        elif risk_score < 0.6:
            return 'MEDIUM'
        else:
            return 'HIGH'
