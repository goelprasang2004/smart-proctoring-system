"""
Enhanced Error Handling Utilities
===================================
Centralized error handling with detailed logging and user-friendly messages.
"""

import traceback
from flask import jsonify
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ApplicationError(Exception):
    """Base exception for application-specific errors"""
    def __init__(self, message, status_code=500, details=None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(ApplicationError):
    """Exception for input validation errors"""
    def __init__(self, message, details=None):
        super().__init__(message, status_code=400, details=details)


class AuthenticationError(ApplicationError):
    """Exception for authentication errors"""
    def __init__(self, message, details=None):
        super().__init__(message, status_code=401, details=details)


class AuthorizationError(ApplicationError):
    """Exception for authorization errors"""
    def __init__(self, message, details=None):
        super().__init__(message, status_code=403, details=details)


class NotFoundError(ApplicationError):
    """Exception for resource not found errors"""
    def __init__(self, message, details=None):
        super().__init__(message, status_code=404, details=details)


class DatabaseError(ApplicationError):
    """Exception for database-related errors"""
    def __init__(self, message, details=None):
        super().__init__(message, status_code=500, details=details)


def handle_error(error, context=None, log_traceback=True):
    """
    Handle and log errors with detailed context.
    
    Args:
        error: Exception object
        context (dict): Additional context information (route, user_id, etc.)
        log_traceback (bool): Whether to log full traceback
        
    Returns:
        tuple: (response_dict, status_code)
    """
    # Default values
    status_code = 500
    error_type = type(error).__name__
    error_message = str(error)
    
    # Build context string
    context_str = ""
    if context:
        context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
    
    # Handle custom application errors
    if isinstance(error, ApplicationError):
        status_code = error.status_code
        logger.error(
            f"{error_type}: {error_message} | Status: {status_code} | Context: {context_str}"
        )
        
        response = {
            'error': error_message,
            'error_type': error_type,
            'status_code': status_code
        }
        
        if error.details:
            response['details'] = error.details
            
        return response, status_code
    
    # Handle ValueError (validation errors)
    elif isinstance(error, ValueError):
        status_code = 400
        logger.warning(
            f"Validation Error: {error_message} | Context: {context_str}"
        )
        
        return {
            'error': error_message,
            'error_type': 'ValidationError',
            'status_code': status_code
        }, status_code
    
    # Handle general exceptions
    else:
        logger.error(
            f"Unhandled {error_type}: {error_message} | Context: {context_str}",
            exc_info=log_traceback
        )
        
        # Log full traceback for debugging
        if log_traceback:
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        return {
            'error': 'An unexpected error occurred',
            'error_type': error_type,
            'status_code': 500,
            'message': error_message  # Include original message for debugging
        }, 500


def log_api_error(endpoint, method, error, user_id=None, request_data=None):
    """
    Log API errors with comprehensive context.
    
    Args:
        endpoint (str): API endpoint path
        method (str): HTTP method
        error: Exception object
        user_id (str): User ID if available
        request_data (dict): Request payload (sensitive data will be masked)
    """
    context = {
        'endpoint': endpoint,
        'method': method,
        'user_id': user_id or 'anonymous'
    }
    
    # Mask sensitive data
    if request_data:
        safe_data = mask_sensitive_data(request_data)
        context['request_data'] = safe_data
    
    logger.error(
        f"API Error in {method} {endpoint} | "
        f"User: {user_id or 'anonymous'} | "
        f"Error: {type(error).__name__}: {str(error)}",
        exc_info=True
    )


def mask_sensitive_data(data):
    """
    Mask sensitive fields in request data for logging.
    
    Args:
        data (dict): Request data
        
    Returns:
        dict: Data with sensitive fields masked
    """
    if not isinstance(data, dict):
        return data
    
    sensitive_fields = ['password', 'token', 'secret', 'api_key', 'refresh_token', 'access_token']
    masked_data = data.copy()
    
    for field in sensitive_fields:
        if field in masked_data:
            masked_data[field] = '***MASKED***'
    
    return masked_data


def validate_required_fields(data, required_fields):
    """
    Validate that all required fields are present in data.
    
    Args:
        data (dict): Data to validate
        required_fields (list): List of required field names
        
    Raises:
        ValidationError: If any required field is missing
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None or data[field] == '']
    
    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}",
            details={'missing_fields': missing_fields}
        )


def validate_uuid(value, field_name='ID'):
    """
    Validate that a value is a valid UUID.
    
    Args:
        value (str): Value to validate
        field_name (str): Name of the field for error message
        
    Raises:
        ValidationError: If value is not a valid UUID
    """
    import uuid
    try:
        uuid.UUID(str(value))
    except (ValueError, AttributeError, TypeError):
        raise ValidationError(f"Invalid {field_name}: must be a valid UUID")


def safe_db_operation(operation, context=None):
    """
    Wrapper for database operations with error handling.
    
    Args:
        operation (callable): Database operation to execute
        context (dict): Context information for logging
        
    Returns:
        Result of the operation
        
    Raises:
        DatabaseError: If database operation fails
    """
    try:
        return operation()
    except Exception as e:
        context_str = str(context) if context else "No context"
        logger.error(f"Database operation failed: {str(e)} | Context: {context_str}", exc_info=True)
        raise DatabaseError(
            "Database operation failed",
            details={'original_error': str(e), 'context': context}
        )


# Error response templates
ERROR_RESPONSES = {
    'INVALID_CREDENTIALS': {
        'error': 'Invalid email or password',
        'error_code': 'AUTH_001'
    },
    'TOKEN_EXPIRED': {
        'error': 'Authentication token has expired',
        'error_code': 'AUTH_002'
    },
    'TOKEN_INVALID': {
        'error': 'Invalid authentication token',
        'error_code': 'AUTH_003'
    },
    'UNAUTHORIZED': {
        'error': 'Unauthorized access',
        'error_code': 'AUTH_004'
    },
    'FORBIDDEN': {
        'error': 'Access forbidden',
        'error_code': 'AUTH_005'
    },
    'NOT_FOUND': {
        'error': 'Resource not found',
        'error_code': 'RES_001'
    },
    'VALIDATION_ERROR': {
        'error': 'Validation error',
        'error_code': 'VAL_001'
    },
    'DATABASE_ERROR': {
        'error': 'Database error occurred',
        'error_code': 'DB_001'
    },
    'SERVER_ERROR': {
        'error': 'Internal server error',
        'error_code': 'SRV_001'
    }
}


def get_error_response(error_type, custom_message=None):
    """
    Get standardized error response.
    
    Args:
        error_type (str): Key from ERROR_RESPONSES
        custom_message (str): Optional custom message to override default
        
    Returns:
        dict: Error response dictionary
    """
    response = ERROR_RESPONSES.get(error_type, ERROR_RESPONSES['SERVER_ERROR']).copy()
    
    if custom_message:
        response['error'] = custom_message
    
    return response
