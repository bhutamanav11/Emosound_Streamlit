import pytest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    with patch.dict(os.environ, {'DATABASE_URL': f'sqlite:///{db_path}'}):
        from database.init_db import initialize_database
        initialize_database()
        yield db_path
    
    os.unlink(db_path)

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit for testing"""
    with patch('streamlit.session_state', {}):
        yield

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword123'
    }

@pytest.fixture
def mock_spotify_api():
    """Mock Spotify API responses"""
    mock_response = {
        'tracks': {
            'items': [
                {
                    'id': 'test_track_id',
                    'name': 'Test Song',
                    'artists': [{'name': 'Test Artist'}],
                    'preview_url': 'https://example.com/preview.mp3',
                    'external_urls': {'spotify': 'https://open.spotify.com/track/test'},
                    'album': {
                        'images': [{'url': 'https://example.com/image.jpg'}]
                    },
                    'duration_ms': 180000,
                    'popularity': 75
                }
            ]
        }
    }
    
    with patch('spotipy.Spotify') as mock_spotify:
        mock_instance = MagicMock()
        mock_instance.search.return_value = mock_response
        mock_spotify.return_value = mock_instance
        yield mock_instance