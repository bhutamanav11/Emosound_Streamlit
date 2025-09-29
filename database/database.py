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
    
    # User operations
    def create_user(self, username, email, password):
        session = self.get_session()
        try:
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
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
        session = self.get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
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