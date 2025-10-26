# ============================================================================
# FIXED api/spotify_api.py - Complete with all required methods
# ============================================================================
"""
Save this as api/spotify_api.py to replace your current version
This includes all required methods for your pages
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import streamlit as st
import requests
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class SpotifyManager:
    def __init__(self):
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        # CRITICAL: Use 127.0.0.1 instead of localhost (Spotify policy April 2025)
        self.redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:8501/')
        
        self.scope = (
            "user-read-playback-state "
            "user-modify-playback-state "
            "user-read-currently-playing "
            "streaming "
            "user-read-private "
            "user-read-email "
            "user-library-read "
            "playlist-read-private "
            "playlist-read-collaborative"
        )
        
        # Initialize public client
        self.public_spotify = None
        self._init_public_client()
    
    def _init_public_client(self):
        """Initialize public Spotify client for search without user auth"""
        try:
            if self.client_id and self.client_secret:
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
                self.public_spotify = spotipy.Spotify(
                    client_credentials_manager=client_credentials_manager
                )
                logger.info("✅ Public Spotify client initialized")
        except Exception as e:
            logger.error(f"❌ Error initializing public client: {e}")
    
    def create_oauth(self):
        """Create SpotifyOAuth object"""
        return SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            cache_path=".spotify_cache",
            show_dialog=False,
            open_browser=False
        )
    
    def get_auth_url(self):
        """Get Spotify authorization URL"""
        try:
            sp_oauth = self.create_oauth()
            auth_url = sp_oauth.get_authorize_url()
            logger.info(f"✅ Generated auth URL: {auth_url[:50]}...")
            return auth_url
        except Exception as e:
            logger.error(f"❌ Error generating auth URL: {e}")
            return None
    
    def get_client(self):
        """Get authenticated client"""
        try:
            # Check cache first
            sp_oauth = self.create_oauth()
            token_info = sp_oauth.get_cached_token()
            
            if token_info:
                if sp_oauth.is_token_expired(token_info):
                    token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
                return spotipy.Spotify(auth=token_info['access_token'])
            
            # Check session state
            if st.session_state.get('spotify_access_token'):
                return spotipy.Spotify(auth=st.session_state['spotify_access_token'])
            
            return None
        except Exception as e:
            logger.error(f"❌ Error getting client: {e}")
            return None
    
    def search_songs_by_emotion(self, emotion, limit=20):
        """Search songs based on emotion (primary method)"""
        try:
            if not self.public_spotify:
                logger.error("Public Spotify client not initialized")
                return []
            
            emotion_queries = {
                'happy': 'happy upbeat positive genre:pop',
                'sad': 'sad melancholy emotional genre:indie',
                'angry': 'angry aggressive rock metal',
                'excited': 'excited energetic party dance',
                'calm': 'calm peaceful relaxing ambient',
                'anxious': 'anxious nervous worried tense',
                'romantic': 'romantic love ballad intimate',
                'energetic': 'energetic upbeat dance workout',
                'melancholic': 'melancholic nostalgic indie folk',
                'confident': 'confident empowering strong motivated',
                'neutral': 'chill mellow easy listening',
                'fear': 'calm soothing peaceful reassuring',
                'surprise': 'exciting unexpected dynamic',
                'disgust': 'calm relaxing peaceful'
            }
            
            query = emotion_queries.get(emotion.lower(), f'{emotion} music')
            
            results = self.public_spotify.search(q=query, type='track', limit=limit, market='US')
            
            songs = []
            for track in results['tracks']['items']:
                spotify_id = track['id']
                
                song_data = {
                    'title': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'spotify_id': spotify_id,
                    'spotify_uri': f"spotify:track:{spotify_id}",
                    'preview_url': track.get('preview_url'),
                    'external_url': f"https://open.spotify.com/track/{spotify_id}",
                    'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'duration_ms': track['duration_ms'],
                    'popularity': track.get('popularity', 0),
                    'album': track['album']['name']
                }
                songs.append(song_data)
            
            logger.info(f"✅ Found {len(songs)} songs for emotion: {emotion}")
            return songs
            
        except Exception as e:
            logger.error(f"❌ Error searching songs: {e}")
            return []
    
    def search_tracks_by_emotion(self, emotion, limit=20):
        """Alias for search_songs_by_emotion (for compatibility)"""
        return self.search_songs_by_emotion(emotion, limit)
    
    def get_user_playlists(self, user_id=None):
        """Get user's Spotify playlists"""
        try:
            client = self.get_client()
            
            if not client:
                logger.warning("No authenticated client available")
                return []
            
            playlists = client.current_user_playlists(limit=50)
            
            playlist_data = []
            for playlist in playlists['items']:
                playlist_data.append({
                    'id': playlist['id'],
                    'name': playlist['name'],
                    'tracks': playlist['tracks'],
                    'external_urls': playlist['external_urls'],
                    'images': playlist['images'],
                    'owner': playlist['owner']['display_name']
                })
            
            logger.info(f"✅ Retrieved {len(playlist_data)} playlists")
            return playlist_data
            
        except Exception as e:
            logger.error(f"❌ Error getting playlists: {e}")
            return []
    
    def get_track_details(self, track_id):
        """Get detailed information about a track"""
        try:
            client = self.public_spotify or self.get_client()
            
            if not client:
                return None
            
            track = client.track(track_id)
            
            return {
                'title': track['name'],
                'artist': ', '.join([artist['name'] for artist in track['artists']]),
                'spotify_id': track['id'],
                'album': track['album']['name'],
                'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'external_url': track['external_urls']['spotify'],
                'preview_url': track.get('preview_url'),
                'duration_ms': track['duration_ms'],
                'popularity': track.get('popularity', 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting track details: {e}")
            return None
    
    def play_track(self, track_uri, device_id=None):
        """Play a track on user's Spotify device (requires Premium)"""
        try:
            client = self.get_client()
            
            if not client:
                return False, "Not authenticated with Spotify"
            
            # Get available devices if no device_id provided
            if not device_id:
                devices = client.devices()
                
                if not devices['devices']:
                    return False, "No active Spotify devices found. Please open Spotify on your phone or computer."
                
                # Find active device or use first available
                for device in devices['devices']:
                    if device['is_active']:
                        device_id = device['id']
                        break
                
                if not device_id:
                    device_id = devices['devices'][0]['id']
            
            # Start playback
            client.start_playback(device_id=device_id, uris=[track_uri])
            
            return True, "Playback started successfully"
            
        except spotipy.exceptions.SpotifyException as e:
            error_msg = str(e)
            if "PREMIUM_REQUIRED" in error_msg or "Premium required" in error_msg:
                return False, "Spotify Premium is required for playback control"
            else:
                return False, f"Playback error: {error_msg}"
        except Exception as e:
            logger.error(f"❌ Error playing track: {e}")
            return False, f"Error: {str(e)}"
    
    def get_recommendations(self, seed_tracks=None, seed_artists=None, seed_genres=None, limit=20, **kwargs):
        """Get Spotify recommendations based on seeds"""
        try:
            client = self.public_spotify or self.get_client()
            
            if not client:
                return []
            
            recommendations = client.recommendations(
                seed_tracks=seed_tracks,
                seed_artists=seed_artists,
                seed_genres=seed_genres,
                limit=limit,
                **kwargs
            )
            
            songs = []
            for track in recommendations['tracks']:
                spotify_id = track['id']
                
                song_data = {
                    'title': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'spotify_id': spotify_id,
                    'spotify_uri': f"spotify:track:{spotify_id}",
                    'preview_url': track.get('preview_url'),
                    'external_url': f"https://open.spotify.com/track/{spotify_id}",
                    'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'duration_ms': track['duration_ms'],
                    'popularity': track.get('popularity', 0),
                    'album': track['album']['name']
                }
                songs.append(song_data)
            
            logger.info(f"✅ Got {len(songs)} recommendations")
            return songs
            
        except Exception as e:
            logger.error(f"❌ Error getting recommendations: {e}")
            return []
    
    def is_authenticated(self):
        """Check if user is authenticated with Spotify"""
        return self.get_client() is not None

# Global instance
spotify_manager = SpotifyManager()