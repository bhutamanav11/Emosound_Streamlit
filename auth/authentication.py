# auth/authentication.py
import streamlit as st
import bcrypt
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AuthManager:
    def __init__(self):
        self.session_timeout = 3600  # 1 hour
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None
        if 'username' not in st.session_state:
            st.session_state.username = None
        if 'login_time' not in st.session_state:
            st.session_state.login_time = None
        if 'spotify_connected' not in st.session_state:
            st.session_state.spotify_connected = False
    
    def hash_password(self, password):
        """Hash password with bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password, hashed_password):
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def login(self, username, password):
        """Authenticate user and create session"""
        try:
            # Import here to avoid circular imports
            from database.database import db_manager
            
            # Get user from database
            session = db_manager.get_session()
            from database.models import User
            user = session.query(User).filter(User.username == username).first()
            
            if user and self.verify_password(password, user.password_hash):
                st.session_state.authenticated = True
                st.session_state.user_id = user.id
                st.session_state.username = user.username
                st.session_state.login_time = datetime.now()
                
                # Check Spotify connection
                if user.spotify_access_token and user.spotify_token_expires:
                    if user.spotify_token_expires > datetime.utcnow():
                        st.session_state.spotify_connected = True
                
                logger.info(f"User logged in: {username}")
                return True
            else:
                logger.warning(f"Failed login attempt for: {username}")
                return False
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def register(self, username, email, password, confirm_password):
        """Register new user"""
        try:
            # Validate inputs
            if not self.validate_registration(username, email, password, confirm_password):
                return False, "Invalid input data"
            
            # Import here to avoid circular imports
            from database.database import db_manager
            from database.models import User
            
            # Check if user exists
            session = db_manager.get_session()
            existing_user = session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                return False, "Username or email already exists"
            
            # Hash password
            hashed_password = self.hash_password(password)
            
            # Create user
            user = User(
                username=username,
                email=email,
                password_hash=hashed_password
            )
            session.add(user)
            session.commit()
            session.close()
            
            logger.info(f"User registered: {username}")
            return True, "Registration successful"
                
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False, f"Registration failed: {str(e)}"
    
    def logout(self):
        """Clear user session"""
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.login_time = None
        st.session_state.spotify_connected = False
        logger.info("User logged out")
    
    def is_authenticated(self):
        """Check if user is authenticated and session is valid"""
        if not st.session_state.get('authenticated', False):
            return False
        
        # Check session timeout
        if st.session_state.get('login_time'):
            if datetime.now() - st.session_state.login_time > timedelta(seconds=self.session_timeout):
                self.logout()
                return False
        
        return True
    
    def require_auth(self):
        """Decorator-like function to require authentication"""
        if not self.is_authenticated():
            st.warning("Please log in to access this page.")
            st.stop()
    
    def validate_registration(self, username, email, password, confirm_password):
        """Validate registration inputs"""
        if len(username) < 3:
            st.error("Username must be at least 3 characters long")
            return False
        
        if len(password) < 6:
            st.error("Password must be at least 6 characters long")
            return False
        
        if password != confirm_password:
            st.error("Passwords do not match")
            return False
        
        if '@' not in email or '.' not in email:
            st.error("Please enter a valid email address")
            return False
        
        return True
    
    def get_current_user(self):
        """Get current authenticated user"""
        if self.is_authenticated():
            try:
                from database.database import db_manager
                from database.models import User
                session = db_manager.get_session()
                user = session.query(User).filter(User.id == st.session_state.user_id).first()
                return user
            except Exception as e:
                logger.error(f"Error getting current user: {e}")
                return None
        return None

# Global auth manager
auth_manager = AuthManager()

# database/database.py - UPDATED
from database.models import *
import bcrypt
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.session = None
    
    def get_session(self):
        if not self.session:
            self.session = get_db_session()
        return self.session
    
    def close_session(self):
        if self.session:
            self.session.close()
            self.session = None
    
    # User operations - FIXED
    def create_user(self, username, email, password):
        """Create user - password hashing handled by auth manager"""
        session = self.get_session()
        try:
            # Import auth manager here to avoid circular import
            from auth.authentication import auth_manager
            
            # Hash password using auth manager
            password_hash = auth_manager.hash_password(password)
            
            user = User(
                username=username,
                email=email,
                password_hash=password_hash
            )
            session.add(user)
            session.commit()
            logger.info(f"User created: {username}")
            return user
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating user: {e}")
            return None
    
    def authenticate_user(self, username, password):
        """Authenticate user - verification handled by auth manager"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if user:
                # Import auth manager here to avoid circular import
                from auth.authentication import auth_manager
                if auth_manager.verify_password(password, user.password_hash):
                    logger.info(f"User authenticated: {username}")
                    return user
            return None
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        session = self.get_session()
        return session.query(User).filter(User.id == user_id).first()
    
    def update_spotify_tokens(self, user_id, access_token, refresh_token, expires_in):
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.spotify_access_token = access_token
                user.spotify_refresh_token = refresh_token
                user.spotify_token_expires = datetime.utcnow() + timedelta(seconds=expires_in)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating Spotify tokens: {e}")
            return False
    
    # Emotion operations
    def get_all_emotions(self):
        session = self.get_session()
        return session.query(Emotion).all()
    
    def get_emotion_by_name(self, name):
        session = self.get_session()
        return session.query(Emotion).filter(Emotion.name.ilike(f"%{name}%")).first()
    
    def create_emotion_log(self, user_id, emotion_id, input_text, input_type, confidence_score):
        session = self.get_session()
        try:
            emotion_log = EmotionLog(
                user_id=user_id,
                emotion_id=emotion_id,
                input_text=input_text,
                input_type=input_type,
                confidence_score=confidence_score
            )
            session.add(emotion_log)
            session.commit()
            return emotion_log
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating emotion log: {e}")
            return None
    
    # Song operations
    def add_or_get_song(self, title, artist, spotify_id=None, preview_url=None, 
                       external_url=None, album_image=None, duration_ms=None, popularity=None):
        session = self.get_session()
        try:
            # Check if song exists
            existing_song = None
            if spotify_id:
                existing_song = session.query(Song).filter(Song.spotify_id == spotify_id).first()
            
            if not existing_song:
                song = Song(
                    title=title,
                    artist=artist,
                    spotify_id=spotify_id,
                    preview_url=preview_url,
                    external_url=external_url,
                    album_image=album_image,
                    duration_ms=duration_ms,
                    popularity=popularity
                )
                session.add(song)
                session.commit()
                return song
            return existing_song
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding song: {e}")
            return None
    
    def log_song_interaction(self, user_id, song_id, emotion_id, input_type, confidence_score, liked=None):
        session = self.get_session()
        try:
            interaction = UserSongHistory(
                user_id=user_id,
                song_id=song_id,
                emotion_id=emotion_id,
                liked=liked,
                input_type=input_type,
                confidence_score=confidence_score
            )
            session.add(interaction)
            session.commit()
            return interaction
        except Exception as e:
            session.rollback()
            logger.error(f"Error logging song interaction: {e}")
            return None
    
    def update_song_feedback(self, user_id, song_id, liked):
        session = self.get_session()
        try:
            # Find the most recent interaction
            interaction = session.query(UserSongHistory).filter(
                UserSongHistory.user_id == user_id,
                UserSongHistory.song_id == song_id
            ).order_by(UserSongHistory.played_at.desc()).first()
            
            if interaction:
                interaction.liked = liked
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating song feedback: {e}")
            return False
    
    # Analytics operations
    def get_user_emotion_history(self, user_id, days=30):
        session = self.get_session()
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return session.query(
            EmotionLog.detected_at,
            Emotion.name,
            Emotion.color_code,
            EmotionLog.confidence_score
        ).join(Emotion).filter(
            EmotionLog.user_id == user_id,
            EmotionLog.detected_at >= cutoff_date
        ).order_by(EmotionLog.detected_at.desc()).all()
    
    def get_user_song_history(self, user_id, limit=50):
        session = self.get_session()
        
        return session.query(
            UserSongHistory.played_at,
            Song.title,
            Song.artist,
            Song.album_image,
            Emotion.name.label('emotion'),
            Emotion.color_code,
            UserSongHistory.liked,
            UserSongHistory.input_type
        ).join(Song).join(Emotion).filter(
            UserSongHistory.user_id == user_id
        ).order_by(UserSongHistory.played_at.desc()).limit(limit).all()
    
    def get_predefined_songs_for_emotion(self, emotion_id, limit=10):
        session = self.get_session()
        
        return session.query(Song).join(PredefinedPlaylist).filter(
            PredefinedPlaylist.emotion_id == emotion_id
        ).order_by(PredefinedPlaylist.priority.desc()).limit(limit).all()

# Global database manager instance
db_manager = DatabaseManager()

# Quick test function to debug login
def test_login_debug(username, password):
    """Debug function to test login process"""
    from auth.authentication import auth_manager
    from database.models import User
    
    session = db_manager.get_session()
    user = session.query(User).filter(User.username == username).first()
    
    if user:
        print(f"User found: {user.username}")
        print(f"Stored hash: {user.password_hash}")
        
        # Test password verification
        result = auth_manager.verify_password(password, user.password_hash)
        print(f"Password verification result: {result}")
        
        # Test with bcrypt directly
        import bcrypt
        direct_result = bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))
        print(f"Direct bcrypt result: {direct_result}")
    else:
        print(f"User not found: {username}")