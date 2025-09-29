import os
import hashlib
import secrets
from functools import wraps
import streamlit as st
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    def __init__(self):
        self.failed_attempts = {}
        self.max_attempts = 5
        self.lockout_duration = 300  # 5 minutes
    
    def hash_password(self, password, salt=None):
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 for password hashing
        import hashlib
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        
        return f"{salt}${hashed.hex()}"
    
    def verify_password(self, password, hashed_password):
        """Verify password against hash"""
        try:
            salt, hash_part = hashed_password.split('$')
            return self.hash_password(password, salt) == hashed_password
        except Exception:
            return False
    
    def check_rate_limit(self, identifier, max_requests=60, window=60):
        """Check if request is within rate limits"""
        now = datetime.now()
        window_start = now - timedelta(seconds=window)
        
        # Clean old entries
        if identifier in self.failed_attempts:
            self.failed_attempts[identifier] = [
                timestamp for timestamp in self.failed_attempts[identifier]
                if timestamp > window_start
            ]
        
        # Check current count
        current_count = len(self.failed_attempts.get(identifier, []))
        
        if current_count >= max_requests:
            return False
        
        # Add current request
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        self.failed_attempts[identifier].append(now)
        return True
    
    def sanitize_input(self, text, max_length=1000):
        """Sanitize user input"""
        if not text:
            return ""
        
        # Truncate to max length
        text = text[:max_length]
        
        # Remove potentially dangerous characters
        import re
        # Allow alphanumeric, spaces, and safe punctuation
        sanitized = re.sub(r'[<>"\']', '', text)
        
        return sanitized.strip()
    
    def validate_file_upload(self, file_obj, allowed_types, max_size_mb=10):
        """Validate uploaded file"""
        if not file_obj:
            return False, "No file provided"
        
        # Check file type
        if file_obj.type not in allowed_types:
            return False, f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
        
        # Check file size
        file_obj.seek(0, os.SEEK_END)
        file_size = file_obj.tell()
        file_obj.seek(0)
        
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            return False, f"File too large. Maximum size: {max_size_mb}MB"
        
        return True, "Valid file"
    
    def generate_csrf_token(self):
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    def validate_csrf_token(self, token):
        """Validate CSRF token"""
        expected_token = st.session_state.get('csrf_token')
        return token == expected_token

def require_auth(func):
    """Decorator to require authentication"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        from auth.authentication import auth_manager
        if not auth_manager.is_authenticated():
            st.warning("Please log in to access this feature.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def rate_limit(max_requests=60, window=60):
    """Decorator to implement rate limiting"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            security = SecurityManager()
            user_id = st.session_state.get('user_id', 'anonymous')
            
            if not security.check_rate_limit(f"user_{user_id}", max_requests, window):
                st.error("Too many requests. Please try again later.")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def secure_headers():
    """Add security headers to response"""
    st.markdown("""
    <script>
    // Add security headers via JavaScript (limited in Streamlit)
    document.addEventListener('DOMContentLoaded', function() {
        // Prevent clickjacking
        if (window.self !== window.top) {
            window.top.location = window.self.location;
        }
    });
    </script>
    """, unsafe_allow_html=True)

# Global security manager
security_manager = SecurityManager()