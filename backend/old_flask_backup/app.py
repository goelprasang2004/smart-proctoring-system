"""
Smart Proctoring System - Main Application Entry Point
======================================================
Industry-grade Flask application with proper configuration,
error handling, and service initialization.

Author: Backend Engineering Team
Created: 2026-01-18
"""

from flask import Flask, jsonify
from flask_cors import CORS
from config.config import Config
from utils.logger import setup_logger
import os

# Initialize logger
logger = setup_logger(__name__)


def create_app(config_class=Config):
    """
    Application Factory Pattern
    
    Creates and configures the Flask application instance.
    This pattern allows for easier testing and multiple app instances.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize CORS with full configuration - allow all origins for development
    CORS(app, 
         resources={r"/api/*": {"origins": "*"}},
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'Accept'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
         expose_headers=['Content-Type', 'Authorization'])
    
    # Manual CORS handling for all responses
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With, Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS')
        return response
    
    # Log application startup
    logger.info("="*60)
    logger.info("Smart Proctoring System - Starting Application")
    logger.info(f"Environment: {app.config['ENV']}")
    logger.info(f"Debug Mode: {app.config['DEBUG']}")
    logger.info("="*60)
    
    # Initialize database connection pool
    try:
        from models.database import get_db_manager
        db_manager = get_db_manager()
        logger.info("[OK] Database connection pool initialized")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        logger.warning("⚠️  Application will start but database operations will fail")
    
    # Register blueprints
    from api.routes.auth import auth_bp
    from api.routes.exams import exams_bp
    from api.routes.exam_assignments import exam_assignments_bp
    from api.routes.proctoring import proctoring_bp
    from api.routes.blockchain import blockchain_bp
    from api.routes.attempts import attempts_bp
    from api.routes.results import results_bp
    from api.routes.admin_routes import admin_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(exams_bp, url_prefix='/api/exams')
    app.register_blueprint(exam_assignments_bp, url_prefix='/api/exams')
    app.register_blueprint(proctoring_bp, url_prefix='/api/proctoring')
    app.register_blueprint(blockchain_bp, url_prefix='/api/blockchain')
    app.register_blueprint(attempts_bp, url_prefix='/api/attempts')
    app.register_blueprint(results_bp, url_prefix='/api/results')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    logger.info("[OK] Authentication routes registered")
    logger.info("[OK] Exam management routes registered")
    logger.info("[OK] Exam assignment routes registered")
    logger.info("[OK] Proctoring routes registered")
    logger.info("[OK] Blockchain routes registered")
    logger.info("[OK] Admin routes registered")

    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring."""
        health_status = {
            'status': 'healthy',
            'service': 'Smart Proctoring System',
            'version': '1.0.0'
        }
        
        # Check database connectivity
        try:
            from models.database import test_database_connection
            db_healthy = test_database_connection()
            health_status['database'] = 'connected' if db_healthy else 'disconnected'
        except Exception as e:
            health_status['database'] = 'error'
            health_status['database_error'] = str(e)
        
        return jsonify(health_status), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint with API info."""
        return jsonify({
            'message': 'Smart Proctoring System API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/health',
                'auth': '/api/auth',
                'exams': '/api/exams'
            }
        }), 200
    
    # Global error handlers
    from utils.error_handlers import (
        ApplicationError, ValidationError, AuthenticationError,
        AuthorizationError, NotFoundError, DatabaseError, handle_error
    )
    
    @app.errorhandler(ApplicationError)
    def handle_application_error(error):
        """Handle custom application errors"""
        response, status_code = handle_error(error, log_traceback=False)
        return jsonify(response), status_code
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle validation errors"""
        response, status_code = handle_error(error, log_traceback=False)
        return jsonify(response), status_code
    
    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(error):
        """Handle authentication errors"""
        response, status_code = handle_error(error, log_traceback=False)
        return jsonify(response), status_code
    
    @app.errorhandler(AuthorizationError)
    def handle_authorization_error(error):
        """Handle authorization errors"""
        response, status_code = handle_error(error, log_traceback=False)
        return jsonify(response), status_code
    
    @app.errorhandler(NotFoundError)
    def handle_notfound_error(error):
        """Handle not found errors"""
        response, status_code = handle_error(error, log_traceback=False)
        return jsonify(response), status_code
    
    @app.errorhandler(DatabaseError)
    def handle_database_error(error):
        """Handle database errors"""
        response, status_code = handle_error(error, log_traceback=True)
        return jsonify(response), status_code
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        logger.warning(f"404 Not Found: {error}")
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'error_code': 'RES_001'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        logger.error(f"Internal Server Error: {error}", exc_info=True)
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'error_code': 'SRV_001'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle all unhandled exceptions"""
        logger.error(f"Unhandled Exception: {type(error).__name__}: {str(error)}", exc_info=True)
        
        # In production, don't expose internal error details
        if app.config.get('DEBUG'):
            return jsonify({
                'error': 'Unhandled Exception',
                'message': str(error),
                'error_type': type(error).__name__,
                'error_code': 'SRV_002'
            }), 500
        else:
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred. Please try again later.',
                'error_code': 'SRV_002'
            }), 500
    
    return app



# Create application instance
app = create_app()


if __name__ == '__main__':
    """Run the application in development mode."""
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
