import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import streamlit as st
import requests
from config import config
from database.database import db_manager
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SpotifyManager:
    def __init__(self):
        self.client_id = config.SPOTIFY_CLIENT_ID
        self.client_secret = config.SPOTIFY_CLIENT_SECRET
        self.redirect_uri = config.SPOTIFY_REDIRECT_URI
        self.scope = "user-read-private user-read-email playlist-read-private user-library-read"
        
        # Client credentials for public API access
        try:
            client_credentials_manager = SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            self.public_spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        except Exception as e:
            logger.error(f"Error initializing Spotify public client: {e}")
            self.public_spotify = None
    
    def get_auth_url(self):
        """Get Spotify authorization URL"""
        try:
            sp_oauth = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope
            )
            auth_url = sp_oauth.get_authorize_url()
            return auth_url
        except Exception as e:
            logger.error(f"Error getting Spotify auth URL: {e}")
            return None
    
    def handle_callback(self, code):
        """Handle Spotify OAuth callback"""
        try:
            sp_oauth = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope
            )
            
            token_info = sp_oauth.get_access_token(code)
            
            if token_info:
                # Store tokens in database
                user_id = st.session_state.get('user_id')
                if user_id:
                    success = db_manager.update_spotify_tokens(
                        user_id,
                        token_info['access_token'],
                        token_info['refresh_token'],
                        token_info['expires_in']
                    )
                    
                    if success:
                        st.session_state.spotify_connected = True
                        logger.info(f"Spotify tokens stored for user {user_id}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling Spotify callback: {e}")
            return False
    
    def get_user_spotify_client(self, user_id):
        """Get authenticated Spotify client for user"""
        try:
            user = db_manager.get_user_by_id(user_id)
            if not user or not user.spotify_access_token:
                return None
            
            # Check if token is expired
            if user.spotify_token_expires and user.spotify_token_expires <= datetime.utcnow():
                # Try to refresh token
                if not self.refresh_user_token(user_id):
                    return None
                # Get updated user
                user = db_manager.get_user_by_id(user_id)
            
            # Create Spotify client
            spotify_client = spotipy.Spotify(auth=user.spotify_access_token)
            return spotify_client
            
        except Exception as e:
            logger.error(f"Error getting user Spotify client: {e}")
            return None
    
    def refresh_user_token(self, user_id):
        """Refresh user's Spotify token"""
        try:
            user = db_manager.get_user_by_id(user_id)
            if not user or not user.spotify_refresh_token:
                return False
            
            sp_oauth = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope
            )
            
            token_info = sp_oauth.refresh_access_token(user.spotify_refresh_token)
            
            if token_info:
                success = db_manager.update_spotify_tokens(
                    user_id,
                    token_info['access_token'],
                    token_info.get('refresh_token', user.spotify_refresh_token),
                    token_info['expires_in']
                )
                return success
            
            return False
            
        except Exception as e:
            logger.error(f"Error refreshing Spotify token: {e}")
            return False
    
    def search_songs_by_emotion(self, emotion, limit=20):
        """Search songs based on emotion using public API"""
        try:
            if not self.public_spotify:
                return []
            
            # Emotion-based search queries
            emotion_queries = {
                'happy': 'happy upbeat positive cheerful',
                'sad': 'sad melancholy emotional heartbreak',
                'angry': 'angry aggressive rock metal',
                'excited': 'excited energetic party dance',
                'calm': 'calm peaceful relaxing ambient',
                'anxious': 'anxious nervous worried tense',
                'romantic': 'romantic love ballad intimate',
                'energetic': 'energetic upbeat dance workout',
                'melancholic': 'melancholic nostalgic indie folk',
                'confident': 'confident empowering strong motivated'
            }
            
            query = emotion_queries.get(emotion.lower(), emotion)
            
            results = self.public_spotify.search(
                q=query,
                type='track',
                limit=limit,
                market='US'
            )
            
            songs = []
            for track in results['tracks']['items']:
                song_data = {
                    'title': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'spotify_id': track['id'],
                    'preview_url': track['preview_url'],
                    'external_url': track['external_urls']['spotify'],
                    'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'duration_ms': track['duration_ms'],
                    'popularity': track['popularity']
                }
                songs.append(song_data)
            
            logger.info(f"Found {len(songs)} songs for emotion: {emotion}")
            return songs
            
        except Exception as e:
            logger.error(f"Error searching songs by emotion: {e}")
            return []
    
    def get_user_playlists(self, user_id):
        """Get user's Spotify playlists"""
        try:
            spotify_client = self.get_user_spotify_client(user_id)
            if not spotify_client:
                return []
            
            playlists = spotify_client.current_user_playlists(limit=50)
            return playlists['items']
            
        except Exception as e:
            logger.error(f"Error getting user playlists: {e}")
            return []
    
    def get_recommendations_for_user(self, user_id, emotion, limit=20):
        """Get personalized recommendations for authenticated user"""
        try:
            spotify_client = self.get_user_spotify_client(user_id)
            if not spotify_client:
                # Fall back to public search
                return self.search_songs_by_emotion(emotion, limit)
            
            # Get user's top tracks for seed
            top_tracks = spotify_client.current_user_top_tracks(limit=5, time_range='medium_term')
            seed_tracks = [track['id'] for track in top_tracks['items'][:2]]
            
            # Emotion-based audio features
            emotion_features = {
                'happy': {'valence': 0.8, 'energy': 0.7, 'danceability': 0.7},
                'sad': {'valence': 0.2, 'energy': 0.3, 'danceability': 0.3},
                'angry': {'valence': 0.3, 'energy': 0.9, 'danceability': 0.5},
                'excited': {'valence': 0.9, 'energy': 0.9, 'danceability': 0.8},
                'calm': {'valence': 0.5, 'energy': 0.2, 'danceability': 0.3},
                'anxious': {'valence': 0.2, 'energy': 0.4, 'danceability': 0.3},
                'romantic': {'valence': 0.6, 'energy': 0.4, 'danceability': 0.5},
                'energetic': {'valence': 0.7, 'energy': 0.9, 'danceability': 0.8},
                'melancholic': {'valence': 0.3, 'energy': 0.3, 'danceability': 0.2},
                'confident': {'valence': 0.8, 'energy': 0.8, 'danceability': 0.6}
            }
            
            features = emotion_features.get(emotion.lower(), {'valence': 0.5, 'energy': 0.5, 'danceability': 0.5})
            
            recommendations = spotify_client.recommendations(
                seed_tracks=seed_tracks,
                limit=limit,
                target_valence=features['valence'],
                target_energy=features['energy'],
                target_danceability=features['danceability']
            )
            
            songs = []
            for track in recommendations['tracks']:
                song_data = {
                    'title': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'spotify_id': track['id'],
                    'preview_url': track['preview_url'],
                    'external_url': track['external_urls']['spotify'],
                    'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'duration_ms': track['duration_ms'],
                    'popularity': track['popularity']
                }
                songs.append(song_data)
            
            logger.info(f"Generated {len(songs)} personalized recommendations for emotion: {emotion}")
            return songs
            
        except Exception as e:
            logger.error(f"Error getting personalized recommendations: {e}")
            # Fall back to public search
            return self.search_songs_by_emotion(emotion, limit)

# Global Spotify manager
spotify_manager = SpotifyManager()