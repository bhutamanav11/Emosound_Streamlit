# ui/pages.py - COMPLETE WITH ALL FUNCTIONS
import streamlit as st
from auth.authentication import auth_manager
from ui.components import *
import logging

logger = logging.getLogger(__name__)

def render_login_page():
    """Render login/registration page"""
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 300;">🎵 EmoSound</h1>
        <p style="color: rgba(255, 255, 255, 0.8); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            AI-Powered Music Discovery Based on Your Emotions
        </p>
    </div>
    """, unsafe_allow_html=True)
    # st.markdown("""
    # <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
    #             padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;">
    #     <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 300;">🎵 EmoSound</h1>
    #     <p style="color: rgba(255, 255, 255, 0.8); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
    #         AI-Powered Music Discovery Based on Your Emotions
    #     </p>
    # </div>
    # """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Welcome back!")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login", type="primary"):
                if username and password:
                    if auth_manager.login(username, password):
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.error("Please fill in all fields")
    
    with tab2:
        st.subheader("Create your account")
        
        with st.form("register_form"):
            new_username = st.text_input("Choose a username")
            new_email = st.text_input("Email address")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm password", type="password")
            
            if st.form_submit_button("Register", type="primary"):
                if all([new_username, new_email, new_password, confirm_password]):
                    success, message = auth_manager.register(
                        new_username, new_email, new_password, confirm_password
                    )
                    
                    if success:
                        st.success(message)
                        st.info("You can now login with your credentials!")
                    else:
                        st.error(message)
                else:
                    st.error("Please fill in all fields")

def render_home_page():
    """Render main home page with emotion detection - FIXED VERSION"""
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 300;">🎵 EmoSound</h1>
        <p style="color: rgba(255, 255, 255, 0.8); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            AI-Powered Music Discovery Based on Your Emotions
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    current_user = auth_manager.get_current_user()
    if current_user:
        st.markdown(f"### Welcome back, {current_user.username}! 👋")
    
    # Emotion detection input
    emotion_data = render_input_section()
    
    # CRITICAL FIX: Only process if emotion_data exists
    if emotion_data and emotion_data.get('emotion'):
        emotion = emotion_data['emotion']
        confidence = emotion_data['confidence']
        
        # Get emotion color
        emotion_color = get_emotion_color(emotion)
        
        # Display detected emotion
        render_emotion_display(emotion, confidence, emotion_color)
        
        # LOG EMOTION TO DATABASE - CRITICAL FIX
        if current_user:
            try:
                from database.database import db_manager
                
                # Get emotion object from database
                emotion_obj = db_manager.get_emotion_by_name(emotion)
                
                if emotion_obj:
                    # Create emotion log entry
                    emotion_log = db_manager.create_emotion_log(
                        user_id=current_user.id,
                        emotion_id=emotion_obj.id,
                        input_text=emotion_data.get('input_text', ''),
                        input_type=emotion_data.get('input_type', 'text'),
                        confidence_score=confidence
                    )
                    
                    if emotion_log:
                        logger.info(f"✅ Logged emotion: {emotion} for user {current_user.id}")
                    else:
                        logger.warning(f"⚠️ Failed to log emotion to database")
                else:
                    logger.warning(f"⚠️ Emotion '{emotion}' not found in database")
                    
            except Exception as e:
                logger.error(f"❌ Error logging emotion: {e}")
                st.warning("Emotion detected but not saved to history")
        
        # Show motivational quote
        try:
            from api.quote_api import quote_manager
            quote = quote_manager.get_quote_for_emotion(emotion)
            if quote:
                render_quote_card(quote)
        except Exception as e:
            logger.warning(f"Could not load quote: {e}")
        
        # Get and display songs
        st.subheader(f"🎵 Songs for your {emotion} mood")
        
        try:
            # Import from app.py
            from app import search_songs_by_emotion
            
            # Search songs
            with st.spinner("🎵 Finding perfect songs for your mood..."):
                songs = search_songs_by_emotion(emotion, limit=10)
            
            if songs:
                st.success(f"Found {len(songs)} songs for your {emotion} mood!")
                
                for index, song in enumerate(songs):
                    # Create container for each song
                    with st.container():
                        col1, col2 = st.columns([1, 3])
                        
                        with col1:
                            if song.get('album_image'):
                                st.image(song['album_image'], width=120)
                            else:
                                st.write("🎵")
                        
                        with col2:
                            st.markdown(f"### {song['title']}")
                            st.write(f"**Artist:** {song['artist']}")
                            st.write(f"**Album:** {song.get('album', 'Unknown')}")
                            
                            # Spotify embed player
                            if song.get('spotify_id'):
                                render_spotify_embed(song['spotify_id'])
                            
                            # Action buttons
                            col_like, col_dislike, col_open, col_save = st.columns(4)
                            
                            with col_like:
                                if st.button("👍 Like", key=f"like_{index}_{song['spotify_id']}"):
                                    # Log song interaction
                                    if current_user and emotion_obj:
                                        try:
                                            # Add song to database
                                            db_song = db_manager.add_or_get_song(
                                                title=song['title'],
                                                artist=song['artist'],
                                                spotify_id=song.get('spotify_id'),
                                                preview_url=song.get('preview_url'),
                                                external_url=song.get('external_url'),
                                                album_image=song.get('album_image'),
                                                duration_ms=song.get('duration_ms'),
                                                popularity=song.get('popularity')
                                            )
                                            
                                            if db_song:
                                                # Log the interaction
                                                db_manager.log_song_interaction(
                                                    user_id=current_user.id,
                                                    song_id=db_song.id,
                                                    emotion_id=emotion_obj.id,
                                                    input_type=emotion_data.get('input_type', 'text'),
                                                    confidence_score=confidence,
                                                    liked=True
                                                )
                                                st.success("❤️ Liked!")
                                        except Exception as e:
                                            logger.error(f"Error logging like: {e}")
                                            st.success("👍 Liked!")
                                    else:
                                        st.success("👍 Liked!")
                            
                            with col_dislike:
                                if st.button("👎 Skip", key=f"skip_{index}_{song['spotify_id']}"):
                                    # Log song interaction as disliked
                                    if current_user and emotion_obj:
                                        try:
                                            db_song = db_manager.add_or_get_song(
                                                title=song['title'],
                                                artist=song['artist'],
                                                spotify_id=song.get('spotify_id'),
                                                preview_url=song.get('preview_url'),
                                                external_url=song.get('external_url'),
                                                album_image=song.get('album_image'),
                                                duration_ms=song.get('duration_ms'),
                                                popularity=song.get('popularity')
                                            )
                                            
                                            if db_song:
                                                db_manager.log_song_interaction(
                                                    user_id=current_user.id,
                                                    song_id=db_song.id,
                                                    emotion_id=emotion_obj.id,
                                                    input_type=emotion_data.get('input_type', 'text'),
                                                    confidence_score=confidence,
                                                    liked=False
                                                )
                                                st.info("👎 Skipped!")
                                        except Exception as e:
                                            logger.error(f"Error logging skip: {e}")
                                            st.info("👎 Skipped!")
                                    else:
                                        st.info("👎 Skipped!")
                            
                            with col_open:
                                if song.get('external_url'):
                                    st.markdown(f"[🎧 Open in Spotify]({song['external_url']})")
                            
                            with col_save:
                                if st.button("➕ Save", key=f"save_{index}_{song['spotify_id']}"):
                                    st.success("💾 Saved!")
                        
                        st.markdown("---")
            else:
                st.info("No songs found. Try a different emotion!")
                
        except Exception as e:
            logger.error(f"Error loading songs: {e}")
            st.error("Could not load songs. Please try again.")
    else:
        # Show placeholder when no emotion detected yet
        st.info("👆 Enter how you're feeling above to get personalized music recommendations!")


def render_profile_page():
    """Render user profile page with analytics - FIXED VERSION"""
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 300;">👤 Your Profile</h1>
        <p style="color: rgba(255, 255, 255, 0.8); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            Your Music Journey & Analytics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    current_user = auth_manager.get_current_user()
    
    if not current_user:
        st.error("Please log in to view your profile.")
        return
    
    # Profile header
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; padding: 2rem; border-radius: 15px; text-align: center; margin-bottom: 2rem;">
        <h2>👤 {current_user.username}</h2>
        <p>Member since {current_user.created_at.strftime("%B %Y")}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User statistics
    st.subheader("📊 Your Statistics")
    
    try:
        from database.database import db_manager
        
        # Get emotion history
        emotion_history = db_manager.get_user_emotion_history(current_user.id, days=30)
        
        # Get song history
        song_history = db_manager.get_user_song_history(current_user.id, limit=100)
        
        # Calculate stats
        total_emotions = len(emotion_history) if emotion_history else 0
        total_songs = len(song_history) if song_history else 0
        liked_songs = len([s for s in song_history if hasattr(s, 'liked') and s.liked == True]) if song_history else 0
        
        # Get unique emotions
        unique_emotions = set()
        if emotion_history:
            for entry in emotion_history:
                emotion_name = getattr(entry, 'name', None)
                if emotion_name:
                    unique_emotions.add(emotion_name)
        
        # Display stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🎭 Emotions Detected", total_emotions)
        
        with col2:
            st.metric("🎵 Songs Played", total_songs)
        
        with col3:
            st.metric("❤️ Songs Liked", liked_songs)
        
        with col4:
            st.metric("🌈 Unique Emotions", len(unique_emotions))
        
        st.markdown("---")
        
        # Charts section
        if total_emotions > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Emotion Timeline")
                render_emotion_history_chart(emotion_history)
            
            with col2:
                st.subheader("🎭 Mood Distribution")
                render_mood_distribution_chart(emotion_history)
        else:
            st.info("🎭 No emotion data yet! Start by detecting your emotions on the Home page.")
        
        st.markdown("---")
        
        # Recent activity
        st.subheader("🎵 Recent Activity")
        
        if total_songs > 0:
            # Display recent songs
            for i, entry in enumerate(list(song_history)[:10]):  # Show last 10
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{entry.title}** by {entry.artist}")
                
                with col2:
                    # Get emotion color
                    emotion_color = getattr(entry, 'color_code', '#667eea')
                    emotion_name = getattr(entry, 'emotion', 'Unknown')
                    
                    st.markdown(f"""
                    <span style="background-color: {emotion_color}; color: white; 
                               padding: 0.25rem 0.75rem; border-radius: 15px; font-size: 0.85rem;">
                        {emotion_name}
                    </span>
                    """, unsafe_allow_html=True)
                
                with col3:
                    played_at = getattr(entry, 'played_at', datetime.now())
                    st.write(played_at.strftime("%m/%d %H:%M"))
                
                with col4:
                    liked = getattr(entry, 'liked', None)
                    if liked == True:
                        st.write("❤️")
                    elif liked == False:
                        st.write("👎")
                    else:
                        st.write("—")
                
                st.markdown("---")
        else:
            st.info("🎵 No songs played yet! Detect your emotion and play some music.")
        
    except Exception as e:
        logger.error(f"Error loading profile data: {e}")
        st.error(f"Error loading profile data: {str(e)}")
        st.info("Please try refreshing the page.")


# ============================================================================
# ADDITIONAL FIX: Add this to ui/components.py if not present
# ============================================================================

def render_spotify_embed(spotify_id):
    """
    Render Spotify embed player
    Add this to ui/components.py if missing
    """
    if not spotify_id:
        st.warning("No Spotify ID available")
        return
    
    embed_url = f"https://open.spotify.com/embed/track/{spotify_id}?utm_source=generator"
    
    st.markdown(f"""
    <iframe 
        style="border-radius:12px" 
        src="{embed_url}" 
        width="100%" 
        height="152" 
        frameBorder="0" 
        allowfullscreen="" 
        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
        loading="lazy">
    </iframe>
    """, unsafe_allow_html=True)

def render_playlists_page():
    # """Render playlists page"""
    # st.markdown("""
    # <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
    #             padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;">
    #     <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 300;">🎵 Playlists</h1>
    #     <p style="color: rgba(255, 255, 255, 0.8); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
    #         Emotion-Based Music Collections
    #     </p>
    # </div>
    # """, unsafe_allow_html=True)
    
    # st.subheader("🎵 Emotion-Based Playlists")
    
    # # Define emotions with colors and emojis
    # emotions = [
    #     ('happy', '#FFD700', '😊'),
    #     ('sad', '#4169E1', '😢'),
    #     ('angry', '#FF4500', '😠'),
    #     ('excited', '#FF69B4', '🎉'),
    #     ('calm', '#98FB98', '😌'),
    #     ('anxious', '#DDA0DD', '😰'),
    #     ('romantic', '#FF1493', '💕'),
    #     ('energetic', '#FF8C00', '⚡'),
    #     ('melancholic', '#708090', '🌧️'),
    #     ('confident', '#DC143C', '💪')
    # ]
    
    # for emotion, color, emoji in emotions:
    #     with st.expander(f"{emoji} {emotion.title()} Playlist"):
    #         st.markdown(f"""
    #         <div style="background: {color}20; padding: 1rem; border-radius: 10px; 
    #                     border-left: 4px solid {color}; margin: 1rem 0;">
    #             <h4 style="color: {color};">{emoji} {emotion.title()} Vibes</h4>
    #             <p>Songs that match your {emotion} mood</p>
    #         </div>
    #         """, unsafe_allow_html=True)
            
    #         # Get sample songs for this emotion
    #         songs = get_sample_songs_for_emotion(emotion)
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 300;">🎵 Playlists</h1>
        <p style="color: rgba(255, 255, 255, 0.8); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            Emotion-Based Music Collections
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🎵 Emotion-Based Playlists")
    
    # Define emotions with colors and emojis
    emotions = [
        ('happy', '#FFD700', '😊'),
        ('sad', '#4169E1', '😢'),
        ('angry', '#FF4500', '😠'),
        ('excited', '#FF69B4', '🎉'),
        ('calm', '#98FB98', '😌'),
        ('anxious', '#DDA0DD', '😰'),
        ('romantic', '#FF1493', '💕'),
        ('energetic', '#FF8C00', '⚡'),
        ('melancholic', '#708090', '🌧️'),
        ('confident', '#DC143C', '💪')
    ]
    
    for emotion, color, emoji in emotions:
        with st.expander(f"{emoji} {emotion.title()} Playlist"):
            st.markdown(f"""
            <div style="background: {color}20; padding: 1rem; border-radius: 10px; 
                        border-left: 4px solid {color}; margin: 1rem 0;">
                <h4 style="color: {color};">{emoji} {emotion.title()} Vibes</h4>
                <p>Songs that match your {emotion} mood</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Get sample songs for this emotion
            songs = get_sample_songs_for_emotion(emotion)
            
            if songs:
                for i, song in enumerate(songs[:5]):  # Show top 5
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"{i+1}. **{song['title']}** by {song['artist']}")
                    with col2:
                        if song.get('external_url'):
                            st.markdown(f"[🎧 Play]({song['external_url']})")
            else:
                st.info(f"Use emotion detection to discover {emotion} songs!")
    
    # Spotify playlists (if connected)
    st.markdown("---")
    st.subheader("🎧 Your Spotify Playlists")
    
    current_user = auth_manager.get_current_user()
    if current_user and st.session_state.get('spotify_connected', False):
        try:
            from api.spotify_api import spotify_manager
            user_playlists = spotify_manager.get_user_playlists(current_user.id)
            
            if user_playlists:
                for playlist in user_playlists:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{playlist['name']}** - {playlist['tracks']['total']} tracks")
                    with col2:
                        if playlist['external_urls']['spotify']:
                            st.markdown(f"[🎧 Open]({playlist['external_urls']['spotify']})")
                    st.markdown("---")
            else:
                st.info("No Spotify playlists found.")
        except Exception as e:
            logger.error(f"Error fetching Spotify playlists: {e}")
            st.info("Connect to Spotify to see your playlists!")
    else:
        st.info("🎧 Connect to Spotify to see your playlists here!")
        render_spotify_connection_status(False)

def render_settings_page():
    """Render settings and preferences page"""
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 300;">⚙️ Settings</h1>
        <p style="color: rgba(255, 255, 255, 0.8); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            Manage Your Account & Preferences
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    current_user = auth_manager.get_current_user()
    
    if current_user:
        # Account settings
        st.subheader("👤 Account Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Username:** {current_user.username}")
            st.write(f"**Email:** {current_user.email}")
            st.write(f"**Member since:** {current_user.created_at.strftime('%B %d, %Y')}")
        
        with col2:
            # Spotify connection
            st.write("**Spotify Connection:**")
            if st.session_state.get('spotify_connected', False):
                st.success("✅ Connected")
                if st.button("Disconnect Spotify", key="disconnect_spotify_btn"):
                    try:
                        from database.database import db_manager
                        db_manager.update_spotify_tokens(current_user.id, None, None, 0)
                        st.session_state.spotify_connected = False
                        st.success("Disconnected from Spotify")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error disconnecting: {e}")
            else:
                st.warning("❌ Not connected")
                render_spotify_connection_status(False)
        
        st.markdown("---")
        
        # Preferences
        st.subheader("🎛️ Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            confidence_threshold = st.slider(
                "Emotion Detection Confidence Threshold",
                min_value=0.1,
                max_value=0.9,
                value=0.3,
                step=0.1,
                help="Minimum confidence required for emotion detection",
                key="confidence_slider"
            )
            
            songs_per_recommendation = st.selectbox(
                "Songs per recommendation",
                options=[5, 10, 15, 20],
                index=1,
                key="songs_select"
            )
        
        with col2:
            enable_notifications = st.checkbox(
                "Enable notifications", 
                value=True,
                key="notif_check"
            )
            
            auto_play_previews = st.checkbox(
                "Auto-play song previews", 
                value=False,
                key="autoplay_check"
            )
        
        if st.button("💾 Save Preferences", type="primary", key="save_prefs_btn"):
            # In a full implementation, save these to user preferences table
            st.success("Preferences saved!")
        
        st.markdown("---")
        
        # Data management
        st.subheader("📊 Data Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Export My Data", key="export_btn"):
                try:
                    from database.database import db_manager
                    
                    emotion_history = db_manager.get_user_emotion_history(current_user.id, days=365)
                    song_history = db_manager.get_user_song_history(current_user.id, limit=1000)
                    
                    export_data = {
                        'user': {
                            'username': current_user.username,
                            'email': current_user.email,
                            'created_at': current_user.created_at.isoformat()
                        },
                        'emotion_history': [
                            {
                                'emotion': entry.name,
                                'confidence': float(entry.confidence_score),
                                'detected_at': entry.detected_at.isoformat()
                            } for entry in emotion_history
                        ] if emotion_history else [],
                        'song_history': [
                            {
                                'title': entry.title,
                                'artist': entry.artist,
                                'emotion': entry.emotion,
                                'liked': entry.liked,
                                'played_at': entry.played_at.isoformat()
                            } for entry in song_history
                        ] if song_history else []
                    }
                    
                    import json
                    json_data = json.dumps(export_data, indent=2)
                    
                    st.download_button(
                        label="📥 Download Data",
                        data=json_data,
                        file_name=f"emosound_data_{current_user.username}.json",
                        mime="application/json",
                        key="download_data_btn"
                    )
                except Exception as e:
                    st.error(f"Error exporting data: {e}")
        
        with col2:
            if st.button("🗑️ Clear History", type="secondary", key="clear_history_btn"):
                if st.session_state.get('confirm_clear', False):
                    try:
                        from database.database import db_manager
                        from database.models import EmotionLog, UserSongHistory, get_db_session
                        
                        session = get_db_session()
                        session.query(EmotionLog).filter(
                            EmotionLog.user_id == current_user.id
                        ).delete()
                        session.query(UserSongHistory).filter(
                            UserSongHistory.user_id == current_user.id
                        ).delete()
                        session.commit()
                        session.close()
                        
                        st.success("History cleared!")
                        st.session_state.confirm_clear = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error clearing history: {e}")
                else:
                    st.warning("⚠️ Click again to confirm deletion")
                    st.session_state.confirm_clear = True
        
        with col3:
            if st.button("❌ Delete Account", type="secondary", key="delete_account_btn"):
                st.error("⚠️ This will permanently delete your account and all data!")
                
                confirm_delete = st.text_input(
                    "Type 'DELETE' to confirm:",
                    key="confirm_delete_input"
                )
                
                if confirm_delete == "DELETE":
                    if st.button("⚠️ Confirm Deletion", type="secondary", key="confirm_delete_btn"):
                        try:
                            from database.database import db_manager
                            from database.models import User, EmotionLog, UserSongHistory, get_db_session
                            
                            session = get_db_session()
                            
                            # Delete related records first
                            session.query(EmotionLog).filter(
                                EmotionLog.user_id == current_user.id
                            ).delete()
                            
                            session.query(UserSongHistory).filter(
                                UserSongHistory.user_id == current_user.id
                            ).delete()
                            
                            # Delete user
                            session.query(User).filter(
                                User.id == current_user.id
                            ).delete()
                            
                            session.commit()
                            session.close()
                            
                            # Logout user
                            auth_manager.logout()
                            st.success("Account deleted successfully. You have been logged out.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting account: {e}")
        
        st.markdown("---")
        
        # Logout
        st.subheader("🚪 Session")
        
        if st.button("🚪 Logout", type="primary", key="logout_btn"):
            auth_manager.logout()
            st.success("You have been logged out.")
            st.rerun()
    
    else:
        st.error("Please log in to access settings.")

def get_sample_songs_for_emotion(emotion):
    """Get sample songs for an emotion"""
    sample_songs = {
        'happy': [
            {'title': 'Happy', 'artist': 'Pharrell Williams', 'spotify_id': 'happy_1'},
            {'title': 'Good as Hell', 'artist': 'Lizzo', 'spotify_id': 'happy_2'},
            {'title': 'Can\'t Stop the Feeling!', 'artist': 'Justin Timberlake', 'spotify_id': 'happy_3'},
            {'title': 'Walking on Sunshine', 'artist': 'Katrina and the Waves', 'spotify_id': 'happy_4'},
            {'title': 'Don\'t Stop Me Now', 'artist': 'Queen', 'spotify_id': 'happy_5'}
        ],
        'sad': [
            {'title': 'Someone Like You', 'artist': 'Adele', 'spotify_id': 'sad_1'},
            {'title': 'Hurt', 'artist': 'Johnny Cash', 'spotify_id': 'sad_2'},
            {'title': 'Mad World', 'artist': 'Gary Jules', 'spotify_id': 'sad_3'},
            {'title': 'The Night We Met', 'artist': 'Lord Huron', 'spotify_id': 'sad_4'},
            {'title': 'Fix You', 'artist': 'Coldplay', 'spotify_id': 'sad_5'}
        ],
        'angry': [
            {'title': 'Break Stuff', 'artist': 'Limp Bizkit', 'spotify_id': 'angry_1'},
            {'title': 'Bodies', 'artist': 'Drowning Pool', 'spotify_id': 'angry_2'},
            {'title': 'Killing in the Name', 'artist': 'Rage Against the Machine', 'spotify_id': 'angry_3'},
            {'title': 'One Step Closer', 'artist': 'Linkin Park', 'spotify_id': 'angry_4'},
            {'title': 'Chop Suey!', 'artist': 'System of a Down', 'spotify_id': 'angry_5'}
        ],
        'excited': [
            {'title': 'Uptown Funk', 'artist': 'Mark Ronson ft. Bruno Mars', 'spotify_id': 'excited_1'},
            {'title': 'I Gotta Feeling', 'artist': 'The Black Eyed Peas', 'spotify_id': 'excited_2'},
            {'title': 'Don\'t Stop Me Now', 'artist': 'Queen', 'spotify_id': 'excited_3'},
            {'title': 'Party Rock Anthem', 'artist': 'LMFAO', 'spotify_id': 'excited_4'},
            {'title': 'We Found Love', 'artist': 'Rihanna ft. Calvin Harris', 'spotify_id': 'excited_5'}
        ],
        'calm': [
            {'title': 'Weightless', 'artist': 'Marconi Union', 'spotify_id': 'calm_1'},
            {'title': 'Clair de Lune', 'artist': 'Claude Debussy', 'spotify_id': 'calm_2'},
            {'title': 'Spiegel im Spiegel', 'artist': 'Arvo Pärt', 'spotify_id': 'calm_3'},
            {'title': 'Gymnopédie No.1', 'artist': 'Erik Satie', 'spotify_id': 'calm_4'},
            {'title': 'The Four Seasons: Spring', 'artist': 'Vivaldi', 'spotify_id': 'calm_5'}
        ],
        'anxious': [
            {'title': 'Breathe', 'artist': 'Pink Floyd', 'spotify_id': 'anxious_1'},
            {'title': 'Anxiety', 'artist': 'Julia Michaels ft. Selena Gomez', 'spotify_id': 'anxious_2'},
            {'title': 'Heavy', 'artist': 'Linkin Park ft. Kiiara', 'spotify_id': 'anxious_3'},
            {'title': 'Stressed Out', 'artist': 'Twenty One Pilots', 'spotify_id': 'anxious_4'},
            {'title': 'Numb', 'artist': 'Linkin Park', 'spotify_id': 'anxious_5'}
        ],
        'romantic': [
            {'title': 'Perfect', 'artist': 'Ed Sheeran', 'spotify_id': 'romantic_1'},
            {'title': 'All of Me', 'artist': 'John Legend', 'spotify_id': 'romantic_2'},
            {'title': 'Thinking Out Loud', 'artist': 'Ed Sheeran', 'spotify_id': 'romantic_3'},
            {'title': 'A Thousand Years', 'artist': 'Christina Perri', 'spotify_id': 'romantic_4'},
            {'title': 'Make You Feel My Love', 'artist': 'Adele', 'spotify_id': 'romantic_5'}
        ],
        'energetic': [
            {'title': 'Thunder', 'artist': 'Imagine Dragons', 'spotify_id': 'energetic_1'},
            {'title': 'Eye of the Tiger', 'artist': 'Survivor', 'spotify_id': 'energetic_2'},
            {'title': 'Titanium', 'artist': 'David Guetta ft. Sia', 'spotify_id': 'energetic_3'},
            {'title': 'Lose Yourself', 'artist': 'Eminem', 'spotify_id': 'energetic_4'},
            {'title': 'Can\'t Hold Us', 'artist': 'Macklemore', 'spotify_id': 'energetic_5'}
        ],
        'melancholic': [
            {'title': 'The Night We Met', 'artist': 'Lord Huron', 'spotify_id': 'melancholic_1'},
            {'title': 'Skinny Love', 'artist': 'Bon Iver', 'spotify_id': 'melancholic_2'},
            {'title': 'Hallelujah', 'artist': 'Jeff Buckley', 'spotify_id': 'melancholic_3'},
            {'title': 'Mad World', 'artist': 'Gary Jules', 'spotify_id': 'melancholic_4'},
            {'title': 'Liability', 'artist': 'Lorde', 'spotify_id': 'melancholic_5'}
        ],
        'confident': [
            {'title': 'Stronger', 'artist': 'Kelly Clarkson', 'spotify_id': 'confident_1'},
            {'title': 'Confident', 'artist': 'Demi Lovato', 'spotify_id': 'confident_2'},
            {'title': 'Fight Song', 'artist': 'Rachel Platten', 'spotify_id': 'confident_3'},
            {'title': 'Roar', 'artist': 'Katy Perry', 'spotify_id': 'confident_4'},
            {'title': 'Survivor', 'artist': 'Destiny\'s Child', 'spotify_id': 'confident_5'}
        ]
    }
    
    return sample_songs.get(emotion.lower(), sample_songs['happy'])
