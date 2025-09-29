import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///emosound.db')
    
    # Spotify API
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8501/callback')
    
    # Quote API
    QUOTE_API_KEY = os.getenv('QUOTE_API_KEY')
    QUOTE_API_URL = os.getenv('QUOTE_API_URL', 'https://api.quotegarden.io/api/v3/quotes')
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
    
    # Application
    APP_NAME = os.getenv('APP_NAME', 'EmoSound')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Session
    SESSION_TIMEOUT = 3600  # 1 hour
    
    # ML Models
    EMOTION_CONFIDENCE_THRESHOLD = 0.3
    MAX_AUDIO_DURATION = 10  # seconds
    
    # UI
    SONGS_PER_PAGE = 10
    HISTORY_DAYS_DEFAULT = 30

config = Config()