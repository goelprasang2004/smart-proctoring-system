"""
AI Analysis Model
=================
Data access layer for AI-generated analysis results.

This module provides database operations for ai_analysis table,
storing AI/ML analysis results for exam attempts.
"""

from models.database import get_db_cursor
from utils.logger import setup_logger
import json

logger = setup_logger(__name__)


class AIAnalysis:
    """
    AI Analysis model for storing AI-generated analysis results.
    
    Analysis types:
    - face_recognition
    - voice_recognition
    - stress_detection
    - behavioral_analysis
    """
    
    @staticmethod
    def create(attempt_id, analysis_type, result_data, anomaly_score=None, recommendations=None):
        """
        Store AI analysis result.
        
        Args:
            attempt_id (str): Exam attempt UUID
            analysis_type (str): Type of AI analysis (from ai_analysis_type ENUM)
            result_data (dict): Analysis results in JSON format
            anomaly_score (float, optional): Anomaly score (0.0 to 1.0)
            recommendations (str, optional): AI-generated recommendations
            
        Returns:
            dict: Created AI analysis record
            
        Raises:
            Exception: If creation fails
        """
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    INSERT INTO ai_analysis (
                        attempt_id, analysis_type, result_data, 
                        anomaly_score, recommendations
                    )
                    VALUES (
                        %s::uuid, %s::ai_analysis_type, %s::jsonb, %s, %s
                    )
                    RETURNING id, attempt_id, analysis_type, result_data, 
                              anomaly_score, recommendations, analyzed_at;
                """, (attempt_id, analysis_type, json.dumps(result_data), anomaly_score, recommendations))
                
                analysis = cursor.fetchone()
                
                logger.info(f"AI analysis stored: {analysis_type} for attempt {attempt_id}")
                
                return {
                    'id': str(analysis[0]),
                    'attempt_id': str(analysis[1]),
                    'analysis_type': analysis[2],
                    'result_data': analysis[3],
                    'anomaly_score': float(analysis[4]) if analysis[4] else None,
                    'recommendations': analysis[5],
                    'analyzed_at': analysis[6].isoformat() if analysis[6] else None
                }
                
        except Exception as e:
            logger.error(f"Failed to create AI analysis: {e}")
            raise
    
    @staticmethod
    def get_by_attempt(attempt_id, analysis_type=None):
        """
        Get all AI analysis results for an exam attempt.
        
        Args:
            attempt_id (str): Exam attempt UUID
            analysis_type (str, optional): Filter by specific analysis type
            
        Returns:
            list: List of AI analysis results
        """
        try:
            if analysis_type:
                query = """
                    SELECT id, attempt_id, analysis_type, result_data, 
                           anomaly_score, recommendations, analyzed_at
                    FROM ai_analysis
                    WHERE attempt_id = %s::uuid
                    AND analysis_type = %s::ai_analysis_type
                    ORDER BY analyzed_at DESC;
                """
                values = (attempt_id, analysis_type)
            else:
                query = """
                    SELECT id, attempt_id, analysis_type, result_data, 
                           anomaly_score, recommendations, analyzed_at
                    FROM ai_analysis
                    WHERE attempt_id = %s::uuid
                    ORDER BY analyzed_at DESC;
                """
                values = (attempt_id,)
            
            with get_db_cursor() as cursor:
                cursor.execute(query, values)
                
                analyses = cursor.fetchall()
                
                return [{
                    'id': str(analysis[0]),
                    'attempt_id': str(analysis[1]),
                    'analysis_type': analysis[2],
                    'result_data': analysis[3],
                    'anomaly_score': float(analysis[4]) if analysis[4] else None,
                    'recommendations': analysis[5],
                    'analyzed_at': analysis[6].isoformat() if analysis[6] else None
                } for analysis in analyses]
                
        except Exception as e:
            logger.error(f"Failed to get AI analysis for attempt {attempt_id}: {e}")
            raise
    
    @staticmethod
    def get_by_id(analysis_id):
        """
        Get AI analysis by ID.
        
        Args:
            analysis_id (str): AI analysis UUID
            
        Returns:
            dict: AI analysis record
            None: If not found
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT id, attempt_id, analysis_type, result_data, 
                           anomaly_score, recommendations, analyzed_at
                    FROM ai_analysis
                    WHERE id = %s::uuid;
                """, (analysis_id,))
                
                analysis = cursor.fetchone()
                
                if not analysis:
                    return None
                
                return {
                    'id': str(analysis[0]),
                    'attempt_id': str(analysis[1]),
                    'analysis_type': analysis[2],
                    'result_data': analysis[3],
                    'anomaly_score': float(analysis[4]) if analysis[4] else None,
                    'recommendations': analysis[5],
                    'analyzed_at': analysis[6].isoformat() if analysis[6] else None
                }
                
        except Exception as e:
            logger.error(f"Failed to get AI analysis {analysis_id}: {e}")
            raise
    
    @staticmethod
    def get_high_anomaly_analyses(anomaly_threshold=0.7):
        """
        Get all AI analyses with high anomaly scores.
        
        Args:
            anomaly_threshold (float): Minimum anomaly score
            
        Returns:
            list: List of high-anomaly analyses with attempt details
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        ai.id, ai.attempt_id, ai.analysis_type, 
                        ai.anomaly_score, ai.recommendations, ai.analyzed_at,
                        ea.exam_id, ea.student_id,
                        u.email as student_email, u.full_name as student_name
                    FROM ai_analysis ai
                    JOIN exam_attempts ea ON ai.attempt_id = ea.id
                    JOIN users u ON ea.student_id = u.id
                    WHERE ai.anomaly_score >= %s
                    ORDER BY ai.anomaly_score DESC, ai.analyzed_at DESC;
                """, (anomaly_threshold,))
                
                analyses = cursor.fetchall()
                
                return [{
                    'id': str(row[0]),
                    'attempt_id': str(row[1]),
                    'analysis_type': row[2],
                    'anomaly_score': float(row[3]) if row[3] else None,
                    'recommendations': row[4],
                    'analyzed_at': row[5].isoformat() if row[5] else None,
                    'exam_id': str(row[6]),
                    'student_id': str(row[7]),
                    'student_email': row[8],
                    'student_name': row[9]
                } for row in analyses]
                
        except Exception as e:
            logger.error(f"Failed to get high anomaly analyses: {e}")
            raise
    
    @staticmethod
    def get_summary_by_attempt(attempt_id):
        """
        Get AI analysis summary for an attempt.
        
        Args:
            attempt_id (str): Exam attempt UUID
            
        Returns:
            dict: Summary statistics
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_analyses,
                        AVG(anomaly_score) as avg_anomaly_score,
                        MAX(anomaly_score) as max_anomaly_score,
                        MIN(anomaly_score) as min_anomaly_score
                    FROM ai_analysis
                    WHERE attempt_id = %s::uuid;
                """, (attempt_id,))
                
                summary = cursor.fetchone()
                
                if not summary or summary[0] == 0:
                    return {
                        'total_analyses': 0,
                        'avg_anomaly_score': None,
                        'max_anomaly_score': None,
                        'min_anomaly_score': None
                    }
                
                return {
                    'total_analyses': summary[0],
                    'avg_anomaly_score': float(summary[1]) if summary[1] else None,
                    'max_anomaly_score': float(summary[2]) if summary[2] else None,
                    'min_anomaly_score': float(summary[3]) if summary[3] else None
                }
                
        except Exception as e:
            logger.error(f"Failed to get AI analysis summary for attempt {attempt_id}: {e}")
            raise
    
    @staticmethod
    def get_analysis_by_type_summary(attempt_id):
        """
        Get analysis count by type for an attempt.
        
        Args:
            attempt_id (str): Exam attempt UUID
            
        Returns:
            list: Analysis counts by type
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        analysis_type,
                        COUNT(*) as count,
                        AVG(anomaly_score) as avg_anomaly_score
                    FROM ai_analysis
                    WHERE attempt_id = %s::uuid
                    GROUP BY analysis_type
                    ORDER BY count DESC;
                """, (attempt_id,))
                
                summary = cursor.fetchall()
                
                return [{
                    'analysis_type': row[0],
                    'count': row[1],
                    'avg_anomaly_score': float(row[2]) if row[2] else None
                } for row in summary]
                
        except Exception as e:
            logger.error(f"Failed to get analysis type summary for attempt {attempt_id}: {e}")
            raise
    
    @staticmethod
    def delete_by_attempt(attempt_id):
        """
        Delete all AI analyses for an attempt.
        
        Args:
            attempt_id (str): Exam attempt UUID
            
        Returns:
            int: Number of analyses deleted
        """
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    DELETE FROM ai_analysis
                    WHERE attempt_id = %s::uuid;
                """, (attempt_id,))
                
                deleted_count = cursor.rowcount
                logger.info(f"Deleted {deleted_count} AI analyses for attempt {attempt_id}")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to delete AI analyses for attempt {attempt_id}: {e}")
            raise
