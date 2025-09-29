import os
import logging
from config import Config

class ProductionConfig(Config):
    DEBUG = False
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/emosound')
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    
    # Logging
    LOG_LEVEL = logging.INFO
    LOG_FILE = '/app/logs/emosound.log'
    
    # Rate limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_PER_MINUTE = 60
    
    # Caching
    CACHE_TTL = 3600  # 1 hour
    CACHE_MAX_SIZE = 1000
    
    # API limits
    SPOTIFY_RATE_LIMIT = 100  # requests per minute
    QUOTE_API_RATE_LIMIT = 50
    
    # Session
    SESSION_TIMEOUT = 7200  # 2 hours
    
    # ML Model settings
    EMOTION_MODEL_CACHE = True
    BATCH_PROCESSING = True

def setup_production_logging():
    """Setup production logging configuration"""
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler('/app/logs/emosound.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_format)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(log_format)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Suppress verbose libraries
    logging.getLogger('transformers').setLevel(logging.WARNING)
    logging.getLogger('torch').setLevel(logging.WARNING)
    logging.getLogger('librosa').setLevel(logging.WARNING)

if __name__ == "__main__":
    setup_production_logging()