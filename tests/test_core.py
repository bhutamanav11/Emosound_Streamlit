import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestEmotionDetection:
    
    def test_text_emotion_detection(self):
        """Test text emotion detection"""
        from emotion.text_emotion import text_emotion_detector
        
        # Test happy emotion
        emotion, confidence = text_emotion_detector.detect_emotion("I am so happy today!")
        assert emotion is not None
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1
    
    def test_emotion_mapping(self):
        """Test emotion mapping to standard categories"""
        from emotion.text_emotion import text_emotion_detector
        
        # Test that detected emotions are mapped properly
        emotion, confidence = text_emotion_detector.detect_emotion("I feel joyful")
        assert emotion in ['happy', 'sad', 'angry', 'excited', 'calm', 'anxious', 'romantic', 'energetic', 'melancholic', 'confident']
    
    def test_empty_text_handling(self):
        """Test handling of empty text input"""
        from emotion.text_emotion import text_emotion_detector
        
        emotion, confidence = text_emotion_detector.detect_emotion("")
        # Should handle gracefully, not crash
        assert emotion is None or isinstance(emotion, str)

class TestDatabaseOperations:
    
    def test_user_creation(self, temp_db, sample_user_data):
        """Test user creation in database"""
        from database.database import db_manager
        
        user = db_manager.create_user(
            sample_user_data['username'],
            sample_user_data['email'],
            sample_user_data['password']
        )
        
        assert user is not None
        assert user.username == sample_user_data['username']
        assert user.email == sample_user_data['email']
    
    def test_user_authentication(self, temp_db, sample_user_data):
        """Test user authentication"""
        from database.database import db_manager
        
        # Create user
        user = db_manager.create_user(
            sample_user_data['username'],
            sample_user_data['email'],
            sample_user_data['password']
        )
        
        # Test authentication
        auth_user = db_manager.authenticate_user(
            sample_user_data['username'],
            sample_user_data['password']
        )
        
        assert auth_user is not None
        assert auth_user.id == user.id
    
    def test_emotion_logging(self, temp_db):
        """Test emotion logging functionality"""
        from database.database import db_manager
        
        # Create test user
        user = db_manager.create_user('testuser', 'test@example.com', 'password')
        
        # Get emotion
        emotion = db_manager.get_emotion_by_name('happy')
        
        # Log emotion
        log_entry = db_manager.create_emotion_log(
            user_id=user.id,
            emotion_id=emotion.id,
            input_text="I am happy!",
            input_type='text',
            confidence_score=0.95
        )
        
        assert log_entry is not None
        assert log_entry.user_id == user.id
        assert log_entry.emotion_id == emotion.id

class TestSpotifyIntegration:
    
    def test_emotion_song_search(self, mock_spotify_api):
        """Test Spotify song search by emotion"""
        from api.spotify_api import spotify_manager
        
        songs = spotify_manager.search_songs_by_emotion('happy', limit=5)
        
        assert isinstance(songs, list)
        assert len(songs) > 0
        
        song = songs[0]
        assert 'title' in song
        assert 'artist' in song
    
    def test_spotify_api_error_handling(self):
        """Test Spotify API error handling"""
        from api.spotify_api import spotify_manager
        
        with patch('spotipy.Spotify') as mock_spotify:
            mock_spotify.side_effect = Exception("API Error")
            
            songs = spotify_manager.search_songs_by_emotion('happy')
            # Should return empty list on error, not crash
            assert songs == []

class TestQuoteAPI:
    
    def test_quote_retrieval(self):
        """Test quote retrieval for emotions"""
        from api.quote_api import quote_manager
        
        quote = quote_manager.get_quote_for_emotion('happy')
        
        assert quote is not None
        assert 'text' in quote
        assert 'author' in quote
        assert 'emotion' in quote
    
    def test_fallback_quotes(self):
        """Test fallback quotes when API fails"""
        from api.quote_api import quote_manager
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            quote = quote_manager.get_quote_for_emotion('happy')
            
            # Should still return a quote from fallback
            assert quote is not None
            assert quote['text']

class TestSecurity:
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        from security import SecurityManager
        
        security = SecurityManager()
        password = "testpassword123"
        
        # Hash password
        hashed = security.hash_password(password)
        
        # Verify correct password
        assert security.verify_password(password, hashed)
        
        # Verify incorrect password
        assert not security.verify_password("wrongpassword", hashed)
    
    def test_input_sanitization(self):
        """Test input sanitization"""
        from security import SecurityManager
        
        security = SecurityManager()
        
        # Test script injection attempt
        malicious_input = "<script>alert('xss')</script>Hello"
        sanitized = security.sanitize_input(malicious_input)
        
        assert "<script>" not in sanitized
        assert "alert" not in sanitized
        assert "Hello" in sanitized
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        from security import SecurityManager
        
        security = SecurityManager()
        identifier = "test_user"
        
        # Should allow initial requests
        for i in range(5):
            assert security.check_rate_limit(identifier, max_requests=10, window=60)
        
        # Should block after limit
        for i in range(20):
            security.check_rate_limit(identifier, max_requests=10, window=60)
        
        # Should be blocked now
        assert not security.check_rate_limit(identifier, max_requests=10, window=60)

class TestUtilities:
    
    def test_time_formatting(self):
        """Test time formatting utilities"""
        from utils.helpers import format_time_ago
        from datetime import datetime, timedelta
        
        # Test recent time
        recent_time = datetime.now() - timedelta(minutes=5)
        formatted = format_time_ago(recent_time)
        assert "minute" in formatted
        
        # Test hours ago
        hours_ago = datetime.now() - timedelta(hours=2)
        formatted = format_time_ago(hours_ago)
        assert "hour" in formatted
    
    def test_email_validation(self):
        """Test email validation"""
        from utils.helpers import validate_email
        
        # Valid emails
        assert validate_email("test@example.com")
        assert validate_email("user.name@domain.co.uk")
        
        # Invalid emails
        assert not validate_email("invalid.email")
        assert not validate_email("@domain.com")
        assert not validate_email("user@")

if __name__ == "__main__":
    pytest.main([__file__])