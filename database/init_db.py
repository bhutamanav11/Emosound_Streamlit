from database.models import create_tables, get_db_session
from database.models import User, Emotion, Song, PredefinedPlaylist
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize database with tables and default data"""
    try:
        # Create tables
        create_tables()
        logger.info("Database tables created successfully")
        
        # Add default emotions
        session = get_db_session()
        
        default_emotions = [
            {"name": "happy", "color_code": "#FFD700", "description": "Feeling joyful and content"},
            {"name": "sad", "color_code": "#4169E1", "description": "Feeling down or melancholic"},
            {"name": "angry", "color_code": "#FF4500", "description": "Feeling frustrated or mad"},
            {"name": "excited", "color_code": "#FF69B4", "description": "Feeling energetic and thrilled"},
            {"name": "calm", "color_code": "#98FB98", "description": "Feeling peaceful and relaxed"},
            {"name": "anxious", "color_code": "#DDA0DD", "description": "Feeling worried or nervous"},
            {"name": "romantic", "color_code": "#FF1493", "description": "Feeling loving and romantic"},
            {"name": "energetic", "color_code": "#FF8C00", "description": "Feeling full of energy"},
            {"name": "melancholic", "color_code": "#708090", "description": "Feeling thoughtfully sad"},
            {"name": "confident", "color_code": "#DC143C", "description": "Feeling self-assured"}
        ]
        
        for emotion_data in default_emotions:
            existing = session.query(Emotion).filter(Emotion.name == emotion_data["name"]).first()
            if not existing:
                emotion = Emotion(**emotion_data)
                session.add(emotion)
        
        session.commit()
        logger.info("Default emotions added successfully")
        
        # Add sample songs for each emotion (you can expand this)
        sample_songs = [
            {"title": "Happy", "artist": "Pharrell Williams", "emotion": "happy"},
            {"title": "Can't Stop the Feeling!", "artist": "Justin Timberlake", "emotion": "happy"},
            {"title": "Someone Like You", "artist": "Adele", "emotion": "sad"},
            {"title": "Hurt", "artist": "Johnny Cash", "emotion": "sad"},
            {"title": "Break Stuff", "artist": "Limp Bizkit", "emotion": "angry"},
            {"title": "Uptown Funk", "artist": "Mark Ronson ft. Bruno Mars", "emotion": "excited"},
            {"title": "Weightless", "artist": "Marconi Union", "emotion": "calm"},
            {"title": "Perfect", "artist": "Ed Sheeran", "emotion": "romantic"},
            {"title": "Thunder", "artist": "Imagine Dragons", "emotion": "energetic"}
        ]
        
        for song_data in sample_songs:
            emotion = session.query(Emotion).filter(Emotion.name == song_data["emotion"]).first()
            if emotion:
                existing_song = session.query(Song).filter(
                    Song.title == song_data["title"],
                    Song.artist == song_data["artist"]
                ).first()
                
                if not existing_song:
                    song = Song(
                        title=song_data["title"],
                        artist=song_data["artist"]
                    )
                    session.add(song)
                    session.commit()
                    
                    # Add to predefined playlist
                    playlist_entry = PredefinedPlaylist(
                        emotion_id=emotion.id,
                        song_id=song.id,
                        priority=1
                    )
                    session.add(playlist_entry)
        
        session.commit()
        session.close()
        logger.info("Sample songs added successfully")
        logger.info("Database initialization completed")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise e

if __name__ == "__main__":
    initialize_database()