import streamlit as st
from datetime import datetime, timedelta
import hashlib
import secrets
import json
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    """Manage user sessions and state"""
    
    def __init__(self):
        self.session_timeout = 3600  # 1 hour
    
    def init_session_state(self):
        """Initialize session state variables"""
        defaults = {
            'authenticated': False,
            'user_id': None,
            'username': None,
            'login_time': None,
            'spotify_connected': False,
            'current_emotion': None,
            'current_songs': [],
            'page_history': [],
            'preferences': {},
            'db_initialized': False
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def set_user_session(self, user_id, username):
        """Set user session data"""
        st.session_state.authenticated = True
        st.session_state.user_id = user_id
        st.session_state.username = username
        st.session_state.login_time = datetime.now()
        
        logger.info(f"Session set for user: {username}")
    
    def clear_session(self):
        """Clear user session"""
        keys_to_clear = [
            'authenticated', 'user_id', 'username', 'login_time',
            'spotify_connected', 'current_emotion', 'current_songs'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        logger.info("User session cleared")
    
    def is_session_valid(self):
        """Check if current session is valid"""
        if not st.session_state.get('authenticated', False):
            return False
        
        login_time = st.session_state.get('login_time')
        if not login_time:
            return False
        
        # Check timeout
        if datetime.now() - login_time > timedelta(seconds=self.session_timeout):
            self.clear_session()
            return False
        
        return True
    
    def extend_session(self):
        """Extend current session"""
        if st.session_state.get('authenticated', False):
            st.session_state.login_time = datetime.now()
    
    def get_session_info(self):
        """Get current session information"""
        if not self.is_session_valid():
            return None
        
        return {
            'user_id': st.session_state.get('user_id'),
            'username': st.session_state.get('username'),
            'login_time': st.session_state.get('login_time'),
            'session_duration': datetime.now() - st.session_state.get('login_time', datetime.now())
        }

class CacheManager:
    """Manage application caching"""
    
    @staticmethod
    @st.cache_data(ttl=300)  # 5 minute cache
    def get_user_emotions(_user_id, days=30):
        """Cached user emotion history"""
        from database.database import db_manager
        return db_manager.get_user_emotion_history(_user_id, days)
    
    @staticmethod
    @st.cache_data(ttl=300)
    def get_user_songs(_user_id, limit=50):
        """Cached user song history"""
        from database.database import db_manager
        return db_manager.get_user_song_history(_user_id, limit)
    
    @staticmethod
    @st.cache_data(ttl=1800)  # 30 minute cache
    def get_spotify_recommendations(_emotion, _limit=10):
        """Cached Spotify recommendations"""
        from api.spotify_api import spotify_manager
        return spotify_manager.search_songs_by_emotion(_emotion, _limit)
    
    @staticmethod
    @st.cache_data(ttl=3600)  # 1 hour cache
    def get_emotion_quote(_emotion):
        """Cached emotion quotes"""
        from api.quote_api import quote_manager
        return quote_manager.get_quote_for_emotion(_emotion)
    
    @staticmethod
    def clear_user_cache(user_id):
        """Clear cache for specific user"""
        CacheManager.get_user_emotions.clear()
        CacheManager.get_user_songs.clear()
    
    @staticmethod
    def clear_all_cache():
        """Clear all application cache"""
        st.cache_data.clear()

class StateManager:
    """Manage application state"""
    
    @staticmethod
    def save_state(key, value):
        """Save state to session"""
        st.session_state[key] = value
    
    @staticmethod
    def load_state(key, default=None):
        """Load state from session"""
        return st.session_state.get(key, default)
    
    @staticmethod
    def delete_state(key):
        """Delete state from session"""
        if key in st.session_state:
            del st.session_state[key]
    
    @staticmethod
    def get_all_state():
        """Get all session state"""
        return dict(st.session_state)
    
    @staticmethod
    def save_user_preferences(user_id, preferences):
        """Save user preferences"""
        st.session_state[f'preferences_{user_id}'] = preferences
    
    @staticmethod
    def load_user_preferences(user_id):
        """Load user preferences"""
        return st.session_state.get(f'preferences_{user_id}', {})

def generate_secure_token():
    """Generate secure random token"""
    return secrets.token_urlsafe(32)

def hash_string(text):
    """Hash string using SHA-256"""
    return hashlib.sha256(text.encode()).hexdigest()

def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.match(pattern, email) is not None

def format_time_ago(dt):
    """Format datetime as time ago"""
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

def sanitize_input(text):
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove potentially harmful characters
    import re
    # Allow letters, numbers, spaces, and basic punctuation
    sanitized = re.sub(r'[^\w\s\.,!?\-\'"()]', '', text)
    return sanitized.strip()

def log_user_action(user_id, action, details=None):
    """Log user actions for analytics"""
    try:
        log_entry = {
            'user_id': user_id,
            'action': action,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'session_id': st.session_state.get('session_id', 'unknown')
        }
        
        # In a production app, this would go to a proper logging system
        logger.info(f"User Action: {json.dumps(log_entry)}")
        
    except Exception as e:
        logger.error(f"Error logging user action: {e}")

# Global instances
session_manager = SessionManager()
cache_manager = CacheManager()
state_manager = StateManager()