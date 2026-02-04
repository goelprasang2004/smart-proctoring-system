"""
Logging Utility Module
======================
Centralized logging configuration for the application.
Provides structured logging with file and console outputs.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logger(name, log_file=None, log_level=None):
    """
    Set up and configure a logger instance.
    
    Creates a logger with both file and console handlers.
    File logs are rotated when they reach 10MB.
    
    Args:
        name (str): Logger name (typically __name__)
        log_file (str): Path to log file (optional)
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Get log level from environment or use provided value
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    # Get log file from environment or use provided value
    if log_file is None:
        log_file = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '%(levelname)s - %(name)s - %(message)s'
    )
    
    # File handler with rotation (10MB max, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Console handler with UTF-8 encoding for Windows compatibility
    import sys
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    # Set encoding to UTF-8 to handle Unicode characters on Windows
    if hasattr(console_handler.stream, 'reconfigure'):
        try:
            console_handler.stream.reconfigure(encoding='utf-8')
        except Exception:
            pass  # If reconfigure fails, continue with default encoding
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log_request(logger, request, response_status=None):
    """
    Log HTTP request details.
    
    Args:
        logger: Logger instance
        request: Flask request object
        response_status (int): HTTP response status code
    """
    logger.info(
        f"{request.method} {request.path} - "
        f"IP: {request.remote_addr} - "
        f"Status: {response_status if response_status else 'N/A'}"
    )


def log_error(logger, error, context=None):
    """
    Log error with context.
    
    Args:
        logger: Logger instance
        error: Exception or error object
        context (dict): Additional context information
    """
    error_msg = f"Error: {str(error)}"
    if context:
        error_msg += f" | Context: {context}"
    
    logger.error(error_msg, exc_info=True)


def log_security_event(logger, event_type, details):
    """
    Log security-related events.
    
    Args:
        logger: Logger instance
        event_type (str): Type of security event
        details (dict): Event details
    """
    logger.warning(
        f"SECURITY EVENT - {event_type}: {details}"
    )


# Create default application logger
app_logger = setup_logger('proctoring_system')
