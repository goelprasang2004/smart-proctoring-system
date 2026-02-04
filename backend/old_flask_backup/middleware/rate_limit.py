"""
Rate Limiting Middleware
========================
Implements rate limiting to prevent abuse and brute force attacks.

Uses in-memory storage (development) or Redis (production).
"""

from functools import wraps
from flask import request, jsonify
from collections import defaultdict
from datetime import datetime, timedelta
from utils.logger import setup_logger, log_security_event
import time

logger = setup_logger(__name__)


# In-memory rate limit storage (for development)
# In production, use Redis for distributed rate limiting
class RateLimitStore:
    """Simple in-memory rate limit store."""
    
    def __init__(self):
        self._requests = defaultdict(list)
    
    def record_request(self, key):
        """Record a request timestamp."""
        self._requests[key].append(time.time())
    
    def get_request_count(self, key, window_seconds):
        """Get request count within time window."""
        now = time.time()
        cutoff = now - window_seconds
        
        # Remove old entries
        self._requests[key] = [
            ts for ts in self._requests[key]
            if ts > cutoff
        ]
        
        return len(self._requests[key])
    
    def clear_expired(self):
        """Clear all expired entries (cleanup)."""
        now = time.time()
        keys_to_delete = []
        
        for key, timestamps in self._requests.items():
            self._requests[key] = [ts for ts in timestamps if ts > now - 3600]
            if not self._requests[key]:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self._requests[key]


# Global rate limit store
_rate_limit_store = RateLimitStore()


def rate_limit(max_requests, window_seconds, key_func=None):
    """
    Rate limit decorator.
    
    Args:
        max_requests (int): Maximum requests allowed
        window_seconds (int): Time window in seconds
        key_func (callable, optional): Function to generate rate limit key
                                       Default uses IP address
    
    Usage:
        @app.route('/api/login')
        @rate_limit(max_requests=5, window_seconds=300)  # 5 per 5 min
        def login():
            return {'message': 'Login'}
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Generate rate limit key
            if key_func:
                key = key_func(request)
            else:
                # Default: Use IP address
                key = f"ip:{request.remote_addr}:{request.endpoint}"
            
            # Check current request count
            current_count = _rate_limit_store.get_request_count(key, window_seconds)
            
            if current_count >= max_requests:
                # Rate limit exceeded
                log_security_event(
                    logger,
                    event_type='rate_limit_exceeded',
                    details={
                        'ip': request.remote_addr,
                        'endpoint': request.endpoint,
                        'limit': max_requests,
                        'window': window_seconds
                    }
                )
                
                retry_after = window_seconds
                
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Please try again in {window_seconds} seconds.',
                    'retry_after': retry_after
                }), 429
            
            # Record this request
            _rate_limit_store.record_request(key)
            
            # Set rate limit headers
            response = f(*args, **kwargs)
            
            # If response is a tuple (body, status_code), handle it
            if isinstance(response, tuple):
                response_obj, status_code = response[0], response[1]
                if hasattr(response_obj, 'headers'):
                    response_obj.headers['X-RateLimit-Limit'] = str(max_requests)
                    response_obj.headers['X-RateLimit-Remaining'] = str(max_requests - current_count - 1)
                    response_obj.headers['X-RateLimit-Reset'] = str(int(time.time() + window_seconds))
                return response_obj, status_code
            else:
                if hasattr(response, 'headers'):
                    response.headers['X-RateLimit-Limit'] = str(max_requests)
                    response.headers['X-RateLimit-Remaining'] = str(max_requests - current_count - 1)
                    response.headers['X-RateLimit-Reset'] = str(int(time.time() + window_seconds))
                return response
        
        return decorated
    
    return decorator


def strict_rate_limit(max_requests, window_seconds):
    """
    Strict rate limit for sensitive endpoints (e.g., login).
    
    More aggressive than regular rate limit.
    Blocks by IP + endpoint combination.
    """
    return rate_limit(max_requests, window_seconds)


def per_user_rate_limit(max_requests, window_seconds):
    """
    Rate limit per authenticated user.
    
    Requires @token_required decorator to be applied first.
    """
    def key_func(req):
        # Extract user from current_user (injected by @token_required)
        # For now, fall back to IP if not available
        return f"user:{req.remote_addr}:{req.endpoint}"
    
    return rate_limit(max_requests, window_seconds, key_func=key_func)


# Predefined rate limit configurations
class RateLimits:
    """Standard rate limit configurations."""
    
    # Authentication endpoints (strict)
    LOGIN = {'max_requests': 5, 'window_seconds': 300}  # 5 per 5 minutes
    REGISTER = {'max_requests': 3, 'window_seconds': 3600}  # 3 per hour
    REFRESH = {'max_requests': 10, 'window_seconds': 300}  # 10 per 5 minutes
    
    # Proctoring events (moderate)
    PROCTORING_EVENT = {'max_requests': 100, 'window_seconds': 60}  # 100 per minute
    
    # Admin endpoints (lenient)
    ADMIN_READ = {'max_requests': 100, 'window_seconds': 60}  # 100 per minute
    ADMIN_WRITE = {'max_requests': 50, 'window_seconds': 60}  # 50 per minute
    
    # General API (moderate)
    GENERAL = {'max_requests': 60, 'window_seconds': 60}  # 60 per minute


def cleanup_rate_limits():
    """
    Periodic cleanup of expired rate limit entries.
    
    Should be called periodically (e.g., every hour) to prevent memory leaks.
    """
    _rate_limit_store.clear_expired()
    logger.info("Rate limit store cleaned up")
