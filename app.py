# ============================================================================
# COMPLETE FIXED app.py - REPLACE YOUR ENTIRE FILE WITH THIS
# ============================================================================

import streamlit as st
import logging
from datetime import datetime
import os
import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables FIRST
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('emosound.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="EmoSound - Emotion-Based Song Recommender",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# SPOTIFY CONFIGURATION - FIXED
# ============================================================================

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:8501')

SPOTIFY_SCOPE = (
    "user-read-private "
    "user-read-email "
    "user-library-read "
    "user-library-modify "
    "user-read-playback-state "
    "user-modify-playback-state "
    "user-read-currently-playing "
    "playlist-read-private "
    "playlist-modify-public "
    "playlist-modify-private "
    "streaming"
)

CACHE_PATH = ".spotify_cache"

def validate_spotify_config():
    """Validate Spotify configuration"""
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        st.error("⚠️ Spotify credentials missing! Check your .env file.")
        st.stop()
        return False
    
    logger.info(f"Spotify Config OK - Redirect: {SPOTIFY_REDIRECT_URI}")
    return True

def get_spotify_oauth():
    """Create SpotifyOAuth instance"""
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE,
        cache_path=CACHE_PATH,
        show_dialog=False,
        open_browser=False
    )

def handle_spotify_callback():
    """Handle Spotify OAuth callback"""
    try:
        query_params = st.query_params
        
        if "code" in query_params:
            auth_code = query_params["code"]
            logger.info(f"✅ Received auth code: {auth_code[:20]}...")
            
            sp_oauth = get_spotify_oauth()
            
            try:
                token_info = sp_oauth.get_access_token(auth_code, as_dict=True, check_cache=False)
                
                if token_info and 'access_token' in token_info:
                    st.session_state['spotify_token_info'] = token_info
                    st.session_state['spotify_access_token'] = token_info['access_token']
                    st.session_state['spotify_refresh_token'] = token_info.get('refresh_token')
                    st.session_state['spotify_authenticated'] = True
                    st.session_state['spotify_connected'] = True
                    
                    logger.info("✅ Successfully obtained access token")
                    
                    if st.session_state.get('user_id'):
                        try:
                            from database.database import db_manager
                            db_manager.update_spotify_tokens(
                                st.session_state.user_id,
                                token_info['access_token'],
                                token_info.get('refresh_token'),
                                token_info.get('expires_in', 3600)
                            )
                        except Exception as e:
                            logger.warning(f"Database save failed: {e}")
                    
                    st.query_params.clear()
                    st.session_state['spotify_just_connected'] = True
                    st.rerun()
                    
                else:
                    logger.error("❌ No access token received")
                    st.error("Failed to get access token")
                    return False
                    
            except Exception as token_error:
                logger.error(f"❌ Token exchange error: {str(token_error)}")
                st.error(f"Authentication failed: {str(token_error)}")
                return False
        
        elif "error" in query_params:
            error = query_params.get("error", "unknown")
            logger.error(f"❌ Spotify auth error: {error}")
            st.error(f"Spotify authorization error: {error}")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Callback error: {str(e)}")
        st.error(f"Error: {str(e)}")
        return False

def get_spotify_client():
    """Get authenticated Spotify client"""
    try:
        # Check session state
        if st.session_state.get('spotify_access_token'):
            try:
                sp = spotipy.Spotify(auth=st.session_state['spotify_access_token'])
                sp.current_user()
                return sp
            except:
                if st.session_state.get('spotify_refresh_token'):
                    try:
                        sp_oauth = get_spotify_oauth()
                        token_info = sp_oauth.refresh_access_token(st.session_state['spotify_refresh_token'])
                        st.session_state['spotify_access_token'] = token_info['access_token']
                        return spotipy.Spotify(auth=token_info['access_token'])
                    except:
                        pass
        
        # Check cache file
        sp_oauth = get_spotify_oauth()
        token_info = sp_oauth.get_cached_token()
        
        if token_info:
            if sp_oauth.is_token_expired(token_info):
                token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            
            st.session_state['spotify_access_token'] = token_info['access_token']
            st.session_state['spotify_authenticated'] = True
            st.session_state['spotify_connected'] = True
            
            return spotipy.Spotify(auth=token_info['access_token'])
        
        # Check database
        if st.session_state.get('user_id'):
            try:
                from database.database import db_manager
                user = db_manager.get_user_by_id(st.session_state.user_id)
                
                if user and user.spotify_access_token:
                    if user.spotify_token_expires and user.spotify_token_expires > datetime.utcnow():
                        st.session_state['spotify_access_token'] = user.spotify_access_token
                        st.session_state['spotify_connected'] = True
                        return spotipy.Spotify(auth=user.spotify_access_token)
            except:
                pass
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting client: {e}")
        return None

def get_spotify_auth_url():
    """Generate Spotify authorization URL"""
    try:
        sp_oauth = get_spotify_oauth()
        auth_url = sp_oauth.get_authorize_url()
        logger.info(f"Generated auth URL: {auth_url}")
        return auth_url
    except Exception as e:
        logger.error(f"Error generating auth URL: {e}")
        return None

def search_songs_by_emotion(emotion, limit=10):
    """Search songs by emotion"""
    try:
        sp = get_spotify_client()
        
        if not sp:
            from spotipy.oauth2 import SpotifyClientCredentials
            sp = spotipy.Spotify(
                client_credentials_manager=SpotifyClientCredentials(
                    client_id=SPOTIFY_CLIENT_ID,
                    client_secret=SPOTIFY_CLIENT_SECRET
                )
            )
        
        emotion_queries = {
            'happy': 'happy upbeat positive',
            'sad': 'sad melancholy emotional',
            'angry': 'angry aggressive intense',
            'excited': 'excited energetic party',
            'calm': 'calm peaceful relaxing',
            'anxious': 'anxious tense',
            'romantic': 'romantic love',
            'energetic': 'energetic upbeat',
            'melancholic': 'melancholic nostalgic',
            'confident': 'confident empowering'
        }
        
        query = emotion_queries.get(emotion.lower(), emotion)
        results = sp.search(q=query, type='track', limit=limit, market='US')
        
        songs = []
        for track in results['tracks']['items']:
            songs.append({
                'title': track['name'],
                'artist': ', '.join([artist['name'] for artist in track['artists']]),
                'spotify_id': track['id'],
                'spotify_uri': track['uri'],
                'preview_url': track.get('preview_url'),
                'external_url': track['external_urls']['spotify'],
                'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'album': track['album']['name'],
                'duration_ms': track['duration_ms'],
                'popularity': track.get('popularity', 0)
            })
        
        logger.info(f"✅ Found {len(songs)} songs for: {emotion}")
        return songs
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return []

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    try:
        validate_spotify_config()
        handle_spotify_callback()
        
        if 'db_initialized' not in st.session_state:
            with st.spinner("Initializing database..."):
                from database.init_db import initialize_database
                initialize_database()
                st.session_state.db_initialized = True
        
        from auth.authentication import auth_manager
        auth_manager.initialize_session_state()
        
        if st.session_state.get('spotify_just_connected'):
            st.balloons()
            st.success("🎉 Spotify connected!")
            del st.session_state.spotify_just_connected
        
        if not auth_manager.is_authenticated():
            from ui.pages import render_login_page
            render_login_page()
            return
        
        render_authenticated_app()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error("An error occurred. Please refresh.")
        if os.getenv('DEBUG', 'False').lower() == 'true':
            st.exception(e)

def render_authenticated_app():
    """Render authenticated app"""
    from ui.pages import render_home_page, render_profile_page, render_playlists_page, render_settings_page
    
    try:
        from streamlit_option_menu import option_menu
        selected = option_menu(
            menu_title=None,
            options=["Home", "Profile", "Playlists", "Settings"],
            icons=["house", "person", "music-note-list", "gear"],
            default_index=0,
            orientation="horizontal",
            key="main_nav"
        )
    except:
        selected = st.selectbox("Navigation", ["Home", "Profile", "Playlists", "Settings"], key="nav")
    
    if selected == "Home":
        render_home_page()
    elif selected == "Profile":
        render_profile_page()
    elif selected == "Playlists":
        render_playlists_page()
    else:
        render_settings_page()
    
    render_sidebar()

def render_sidebar():
    """Render sidebar"""
    with st.sidebar:
        st.header("🎵 EmoSound")
        
        from auth.authentication import auth_manager
        current_user = auth_manager.get_current_user()
        
        if current_user:
            st.write(f"**{current_user.username}**")
            
            sp_client = get_spotify_client()
            
            if sp_client:
                st.success("🎧 Connected")
                st.session_state['spotify_connected'] = True
                
                if st.button("🔌 Disconnect", key="disconnect", use_container_width=True):
                    if os.path.exists(CACHE_PATH):
                        os.remove(CACHE_PATH)
                    
                    for key in ['spotify_token_info', 'spotify_access_token', 'spotify_refresh_token', 
                               'spotify_authenticated', 'spotify_connected']:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    if st.session_state.get('user_id'):
                        try:
                            from database.database import db_manager
                            db_manager.update_spotify_tokens(st.session_state.user_id, None, None, 0)
                        except:
                            pass
                    
                    st.rerun()
                    
            else:
                st.warning("🎧 Not Connected")
                st.session_state['spotify_connected'] = False
                
                if st.button("🎵 Connect Spotify", key="connect", use_container_width=True, type="primary"):
                    auth_url = get_spotify_auth_url()
                    if auth_url:
                        st.markdown(f"""
                        <meta http-equiv="refresh" content="0; url={auth_url}">
                        <p>Redirecting...</p>
                        <p><a href="{auth_url}" target="_self">Click here if not redirected</a></p>
                        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.write("**About**")
        st.caption("AI music recommendations")
        st.caption("Version: 1.0.0")

if __name__ == "__main__":
    main()