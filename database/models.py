from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    spotify_access_token = Column(String(255), nullable=True)
    spotify_refresh_token = Column(String(255), nullable=True)
    spotify_token_expires = Column(DateTime, nullable=True)
    
    # Relationships
    song_history = relationship("UserSongHistory", back_populates="user")
    emotion_logs = relationship("EmotionLog", back_populates="user")

class Emotion(Base):
    __tablename__ = 'emotions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    color_code = Column(String(7), nullable=False)  # Hex color
    description = Column(Text, nullable=True)
    
    # Relationships
    emotion_logs = relationship("EmotionLog", back_populates="emotion")
    predefined_playlists = relationship("PredefinedPlaylist", back_populates="emotion")

class Song(Base):
    __tablename__ = 'songs'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    artist = Column(String(200), nullable=False)
    spotify_id = Column(String(100), unique=True, nullable=True)
    preview_url = Column(String(500), nullable=True)
    external_url = Column(String(500), nullable=True)
    album_image = Column(String(500), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    popularity = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    song_history = relationship("UserSongHistory", back_populates="song")
    playlist_songs = relationship("PredefinedPlaylist", back_populates="song")

class UserSongHistory(Base):
    __tablename__ = 'user_song_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    song_id = Column(Integer, ForeignKey('songs.id'), nullable=False)
    emotion_id = Column(Integer, ForeignKey('emotions.id'), nullable=False)
    liked = Column(Boolean, default=None)  # True=liked, False=disliked, None=no feedback
    played_at = Column(DateTime, default=datetime.utcnow)
    input_type = Column(String(20), nullable=False)  # 'text', 'audio_file', 'live_audio'
    confidence_score = Column(Float, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="song_history")
    song = relationship("Song", back_populates="song_history")
    emotion = relationship("Emotion")

class EmotionLog(Base):
    __tablename__ = 'emotion_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    emotion_id = Column(Integer, ForeignKey('emotions.id'), nullable=False)
    input_text = Column(Text, nullable=True)
    input_type = Column(String(20), nullable=False)
    confidence_score = Column(Float, nullable=False)
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="emotion_logs")
    emotion = relationship("Emotion", back_populates="emotion_logs")

class PredefinedPlaylist(Base):
    __tablename__ = 'predefined_playlists'
    
    id = Column(Integer, primary_key=True)
    emotion_id = Column(Integer, ForeignKey('emotions.id'), nullable=False)
    song_id = Column(Integer, ForeignKey('songs.id'), nullable=False)
    priority = Column(Integer, default=0)  # Higher priority songs shown first
    
    # Relationships
    emotion = relationship("Emotion", back_populates="predefined_playlists")
    song = relationship("Song", back_populates="playlist_songs")

# Database engine and session
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///emosound.db')
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    session = SessionLocal()
    try:
        return session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        pass  # Don't close here, let caller handle it

def create_tables():
    Base.metadata.create_all(bind=engine)


    