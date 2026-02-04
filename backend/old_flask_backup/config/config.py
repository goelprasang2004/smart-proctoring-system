"""
Configuration Module
===================
Centralized configuration management using environment variables.
Follows the 12-factor app methodology.

Environment variables are loaded from .env file.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Base configuration class.
    
    All configuration values are loaded from environment variables
    with sensible defaults where appropriate.
    """
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'proctoring_system')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Database Pool Configuration
    DB_POOL_MIN = int(os.getenv('DB_POOL_MIN', '2'))
    DB_POOL_MAX = int(os.getenv('DB_POOL_MAX', '10'))
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', '2592000'))  # 30 days
    
    # Security Configuration
    BCRYPT_ROUNDS = int(os.getenv('BCRYPT_ROUNDS', '12'))
    
    # CORS Configuration
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # AI Module Configuration (for future steps)
    AI_FACE_RECOGNITION_ENABLED = os.getenv('AI_FACE_RECOGNITION_ENABLED', 'True').lower() == 'true'
    AI_VOICE_RECOGNITION_ENABLED = os.getenv('AI_VOICE_RECOGNITION_ENABLED', 'True').lower() == 'true'
    AI_STRESS_DETECTION_ENABLED = os.getenv('AI_STRESS_DETECTION_ENABLED', 'True').lower() == 'true'
    
    # Blockchain Configuration (for future steps)
    BLOCKCHAIN_DIFFICULTY = int(os.getenv('BLOCKCHAIN_DIFFICULTY', '4'))
    
    # File Upload Configuration (for future steps)
    MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', '10485760'))  # 10MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    
    @staticmethod
    def validate():
        """
        Validate critical configuration values.
        
        Raises:
            ValueError: If critical configuration is missing
        """
        if not Config.SECRET_KEY or Config.SECRET_KEY == 'dev-secret-key-change-in-production':
            if Config.ENV == 'production':
                raise ValueError("SECRET_KEY must be set in production environment")
        
        if not Config.DB_PASSWORD:
            print("⚠️  WARNING: DB_PASSWORD is not set. Database connection may fail.")
        
        if Config.ENV == 'production' and Config.DEBUG:
            print("⚠️  WARNING: DEBUG mode is enabled in production. This is a security risk.")


class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True
    ENV = 'development'


class ProductionConfig(Config):
    """Production-specific configuration."""
    DEBUG = False
    ENV = 'production'


class TestingConfig(Config):
    """Testing-specific configuration."""
    TESTING = True
    DEBUG = True


# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """
    Get configuration object based on environment.
    
    Args:
        env (str): Environment name (development, production, testing)
        
    Returns:
        Config: Configuration object
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    return config.get(env, config['default'])
