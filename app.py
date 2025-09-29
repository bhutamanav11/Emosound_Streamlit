import streamlit as st
import logging
from datetime import datetime
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

# Import application modules
from config import config
from auth.authentication import auth_manager
from ui.pages import *
from ui.components import render_navigation_menu
from database.init_db import initialize_database
from database.database import db_manager

# Page configuration
st.set_page_config(
    page_title="EmoSound - Emotion-Based Song Recommender",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    """Main application entry point"""
    try:
        # Initialize database on first run
        if 'db_initialized' not in st.session_state:
            with st.spinner("Initializing database..."):
                initialize_database()
                st.session_state.db_initialized = True
            logger.info("Database initialized successfully")
        
        # Initialize authentication
        auth_manager.initialize_session_state()
        
        # Check authentication status
        if not auth_manager.is_authenticated():
            render_login_page()
            return
        
        # Main authenticated application
        render_authenticated_app()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error("An error occurred. Please refresh the page and try again.")
        
        if config.DEBUG:
            st.exception(e)

def render_authenticated_app():
    """Render the main authenticated application"""
    
    # Navigation
    selected_page = render_navigation_menu()
    
    # Route to appropriate page
    if selected_page == "Home":
        render_home_page()
    elif selected_page == "Profile":
        render_profile_page()
    elif selected_page == "Playlists":
        render_playlists_page()
    elif selected_page == "Settings":
        render_settings_page()
    
    # Sidebar information
    render_sidebar()

def render_sidebar():
    """Render sidebar with additional information"""
    with st.sidebar:
        st.header("🎵 EmoSound")
        
        # Current user info
        current_user = auth_manager.get_current_user()
        if current_user:
            st.write(f"Welcome, **{current_user.username}**!")
            
            # Quick stats
            emotion_history = db_manager.get_user_emotion_history(st.session_state.user_id, days=7)
            st.metric("Emotions This Week", len(emotion_history))
            
            song_history = db_manager.get_user_song_history(st.session_state.user_id, limit=50)
            recent_songs = len([s for s in song_history if (datetime.now() - s.played_at).days <= 7])
            st.metric("Songs This Week", recent_songs)
        
        st.markdown("---")
        
        # Quick actions
        st.subheader("Quick Actions")
        
        if st.button("🎭 Detect Emotion", key="sidebar_emotion"):
            st.session_state.show_emotion_input = True
        
        if st.button("🎵 Browse Playlists", key="sidebar_playlists"):
            st.session_state.current_page = "Playlists"
        
        if not st.session_state.get('spotify_connected', False):
            if st.button("🎧 Connect Spotify", key="sidebar_spotify"):
                from api.spotify_api import spotify_manager
                auth_url = spotify_manager.get_auth_url()
                if auth_url:
                    st.markdown(f"[Connect to Spotify]({auth_url})")
        
        st.markdown("---")
        
        # App information
        st.subheader("About")
        st.write("""
        EmoSound uses AI to detect your emotions and recommend music that matches your mood.
        
        **Features:**
        - Text emotion detection
        - Audio emotion detection
        - Spotify integration
        - Personalized recommendations
        - Mood analytics
        """)
        
        st.markdown("---")
        
        # Version and links
        st.write("**Version:** 1.0.0")
        st.write("**Built with:** Streamlit, Transformers, Spotify API")
        
        # Footer
        st.markdown("""
        <div style="text-align: center; color: #888; font-size: 0.8rem; margin-top: 2rem;">
            Made with ❤️ for music lovers
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()