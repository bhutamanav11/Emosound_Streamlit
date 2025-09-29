import streamlit as st
from auth.authentication import auth_manager
from ui.components import *
from ui.styles import get_custom_css
from ui.components import render_app_header, render_spotify_connection_status, render_emotion_display, render_quote_card, render_song_card, render_mood_distribution_chart, render_emotion_history_chart
from database.database import db_manager
from api.spotify_api import spotify_manager
from api.quote_api import quote_manager
from emotion.emotion_utils import emotion_utils
import logging

logger = logging.getLogger(__name__)

def render_login_page():
    """Render login/registration page"""
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    render_app_header()
    
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
    """Render main home page with emotion detection and song recommendations"""
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    render_app_header()
    
    # User greeting
    current_user = auth_manager.get_current_user()
    st.markdown(f"### Welcome back, {current_user.username}! 👋")
    
    # Spotify connection status
    render_spotify_connection_status(st.session_state.get('spotify_connected', False))
    
    # Handle Spotify callback
    query_params = st.experimental_get_query_params()
    if 'code' in query_params:
        code = query_params['code'][0]
        if spotify_manager.handle_callback(code):
            st.success("Successfully connected to Spotify!")
            st.experimental_set_query_params()
            st.rerun()
        else:
            st.error("Failed to connect to Spotify")
    
    # Emotion input section
    emotion_data = render_input_section()
    
    if emotion_data and emotion_data['emotion']:
        # Display detected emotion
        emotion_color = emotion_utils.get_emotion_color(emotion_data['emotion'])
        render_emotion_display(
            emotion_data['emotion'],
            emotion_data['confidence'],
            emotion_color
        )
        
        # Log emotion detection
        emotion_log = db_manager.create_emotion_log(
            user_id=st.session_state.user_id,
            emotion_id=db_manager.get_emotion_by_name(emotion_data['emotion']).id,
            input_text=emotion_data.get('input_text'),
            input_type=emotion_data['input_type'],
            confidence_score=emotion_data['confidence']
        )
        
        # Get motivational quote
        quote_data = quote_manager.get_quote_for_emotion(emotion_data['emotion'])
        render_quote_card(quote_data)
        
        # Get song recommendations
        st.subheader("🎵 Songs for your mood")
        
        with st.spinner("Finding perfect songs for you..."):
            # Get songs from Spotify
            if st.session_state.get('spotify_connected', False):
                songs = spotify_manager.get_recommendations_for_user(
                    st.session_state.user_id,
                    emotion_data['emotion'],
                    limit=10
                )
            else:
                songs = spotify_manager.search_songs_by_emotion(
                    emotion_data['emotion'],
                    limit=10
                )
            
            # Get predefined songs from database
            emotion_obj = db_manager.get_emotion_by_name(emotion_data['emotion'])
            if emotion_obj:
                db_songs = db_manager.get_predefined_songs_for_emotion(emotion_obj.id, limit=5)
                
                # Convert to same format
                for db_song in db_songs:
                    song_data = {
                        'title': db_song.title,
                        'artist': db_song.artist,
                        'spotify_id': db_song.spotify_id,
                        'preview_url': db_song.preview_url,
                        'external_url': db_song.external_url,
                        'album_image': db_song.album_image,
                        'duration_ms': db_song.duration_ms,
                        'popularity': db_song.popularity
                    }
                    songs.insert(0, song_data)  # Add to beginning
        
        if songs:
            for song in songs:
                # Add song to database if not exists
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
                    # Log song interaction
                    db_manager.log_song_interaction(
                        user_id=st.session_state.user_id,
                        song_id=db_song.id,
                        emotion_id=emotion_obj.id if emotion_obj else None,
                        input_type=emotion_data['input_type'],
                        confidence_score=emotion_data['confidence']
                    )
                    
                    # Render song card with feedback options
                    def handle_like(song_data):
                        db_manager.update_song_feedback(
                            st.session_state.user_id,
                            db_song.id,
                            True
                        )
                        st.success("👍 Glad you liked it!")
                    
                    def handle_dislike(song_data):
                        db_manager.update_song_feedback(
                            st.session_state.user_id,
                            db_song.id,
                            False
                        )
                        st.info("👎 Thanks for the feedback!")
                    
                    render_song_card(
                        song,
                        emotion_color,
                        st.session_state.user_id,
                        on_like=handle_like,
                        on_dislike=handle_dislike
                    )
        else:
            st.info("No songs found for this emotion. Try a different input!")

def render_home_page():
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 300;">🎵 EmoSound</h1>
        <p style="color: rgba(255, 255, 255, 0.8); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            Discover music that matches your emotions
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    current_user = auth_manager.get_current_user()
    if current_user:
        st.markdown(f"### Welcome back, {current_user.username}! 👋")
    
    # Emotion detection
    emotion_data = render_input_section()
    
    if emotion_data and emotion_data['emotion']:
        # Display detected emotion
        emotion_color = get_emotion_color(emotion_data['emotion'])
        render_emotion_display(
            emotion_data['emotion'],
            emotion_data['confidence'],
            emotion_color
        )
        
        # Get sample songs for the emotion
        st.subheader(f"🎵 Songs for your {emotion_data['emotion']} mood")
        
        sample_songs = get_sample_songs_for_emotion(emotion_data['emotion'])
        
        if sample_songs:
            for index, song in enumerate(sample_songs):
                # Handle like/dislike actions
                def handle_like(song_data, idx=index):
                    st.success(f"👍 Glad you liked {song_data['title']}!")
                
                def handle_dislike(song_data, idx=index):
                    st.info(f"👎 Thanks for the feedback on {song_data['title']}!")
                
                # Render song card with unique index
                render_song_card(
                    song,
                    emotion_color,
                    current_user.id if current_user else 'guest',
                    on_like=lambda s, i=index: handle_like(s, i),
                    on_dislike=lambda s, i=index: handle_dislike(s, i),
                    card_index=index  # This ensures unique keys
                )
        else:
            st.info("No songs found for this emotion. Try a different mood!")

def get_sample_songs_for_emotion(emotion):
    """Get sample songs for an emotion"""
    sample_songs = {
        'happy': [
            {'title': 'Happy', 'artist': 'Pharrell Williams', 'spotify_id': 'happy_1'},
            {'title': 'Good as Hell', 'artist': 'Lizzo', 'spotify_id': 'happy_2'},
            {'title': 'Can\'t Stop the Feeling!', 'artist': 'Justin Timberlake', 'spotify_id': 'happy_3'}
        ],
        'sad': [
            {'title': 'Someone Like You', 'artist': 'Adele', 'spotify_id': 'sad_1'},
            {'title': 'Hurt', 'artist': 'Johnny Cash', 'spotify_id': 'sad_2'},
            {'title': 'Mad World', 'artist': 'Gary Jules', 'spotify_id': 'sad_3'}
        ],
        'angry': [
            {'title': 'Break Stuff', 'artist': 'Limp Bizkit', 'spotify_id': 'angry_1'},
            {'title': 'Bodies', 'artist': 'Drowning Pool', 'spotify_id': 'angry_2'},
            {'title': 'Killing in the Name', 'artist': 'Rage Against the Machine', 'spotify_id': 'angry_3'}
        ],
        'calm': [
            {'title': 'Weightless', 'artist': 'Marconi Union', 'spotify_id': 'calm_1'},
            {'title': 'Clair de Lune', 'artist': 'Claude Debussy', 'spotify_id': 'calm_2'},
            {'title': 'On Earth as It Is in Heaven', 'artist': 'Max Richter', 'spotify_id': 'calm_3'}
        ],
        'anxious': [
            {'title': 'Breathe', 'artist': 'Pink Floyd', 'spotify_id': 'anxious_1'},
            {'title': 'Anxiety', 'artist': 'Julia Michaels', 'spotify_id': 'anxious_2'},
            {'title': 'Heavy', 'artist': 'Linkin Park', 'spotify_id': 'anxious_3'}
        ],
        'excited': [
            {'title': 'Uptown Funk', 'artist': 'Mark Ronson ft. Bruno Mars', 'spotify_id': 'excited_1'},
            {'title': 'I Gotta Feeling', 'artist': 'The Black Eyed Peas', 'spotify_id': 'excited_2'},
            {'title': 'Don\'t Stop Me Now', 'artist': 'Queen', 'spotify_id': 'excited_3'}
        ],
        'romantic': [
            {'title': 'Perfect', 'artist': 'Ed Sheeran', 'spotify_id': 'romantic_1'},
            {'title': 'All of Me', 'artist': 'John Legend', 'spotify_id': 'romantic_2'},
            {'title': 'Thinking Out Loud', 'artist': 'Ed Sheeran', 'spotify_id': 'romantic_3'}
        ],
        'confident': [
            {'title': 'Stronger', 'artist': 'Kelly Clarkson', 'spotify_id': 'confident_1'},
            {'title': 'Confident', 'artist': 'Demi Lovato', 'spotify_id': 'confident_2'},
            {'title': 'Fight Song', 'artist': 'Rachel Platten', 'spotify_id': 'confident_3'}
        ]
    }
    
    return sample_songs.get(emotion.lower(), sample_songs['happy'])
def render_playlists_page():
    """Render playlists page"""
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    render_app_header()
    
    st.subheader("🎵 Your Playlists")
    
    # Emotion-based playlists
    st.write("### Emotion Playlists")
    
    emotions = db_manager.get_all_emotions()
    
    for emotion in emotions:
        with st.expander(f"{emotion.name.title()} Playlist", expanded=False):
            songs = db_manager.get_predefined_songs_for_emotion(emotion.id, limit=20)
            
            if songs:
                for song in songs:
                    song_data = {
                        'title': song.title,
                        'artist': song.artist,
                        'spotify_id': song.spotify_id,
                        'preview_url': song.preview_url,
                        'external_url': song.external_url,
                        'album_image': song.album_image,
                        'duration_ms': song.duration_ms,
                        'popularity': song.popularity
                    }
                    render_song_card(song_data, emotion.color_code, st.session_state.user_id, show_actions=False)
            else:
                st.info(f"No songs available for {emotion.name} yet.")
    
    # Spotify playlists (if connected)
    if st.session_state.get('spotify_connected', False):
        st.write("### Your Spotify Playlists")
        
        user_playlists = spotify_manager.get_user_playlists(st.session_state.user_id)
        
        if user_playlists:
            for playlist in user_playlists:
                st.write(f"**{playlist['name']}** - {playlist['tracks']['total']} tracks")
                if playlist['external_urls']['spotify']:
                    st.markdown(f"[Open in Spotify]({playlist['external_urls']['spotify']})")
                st.markdown("---")
        else:
            st.info("No Spotify playlists found.")

def render_settings_page():
    """Render settings and preferences page"""
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    render_app_header()
    
    st.subheader("⚙️ Settings")
    
    current_user = auth_manager.get_current_user()
    
    # Account settings
    st.write("### Account Settings")
    
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
            if st.button("Disconnect Spotify"):
                # Clear Spotify tokens
                db_manager.update_spotify_tokens(st.session_state.user_id, None, None, 0)
                st.session_state.spotify_connected = False
                st.success("Disconnected from Spotify")
                st.rerun()
        else:
            st.warning("❌ Not connected")
            render_spotify_connection_status(False)
    
    st.markdown("---")
    
    # Preferences
    st.write("### Preferences")
    
    # These would be stored in user preferences table in a full implementation
    col1, col2 = st.columns(2)
    
    with col1:
        confidence_threshold = st.slider(
            "Emotion Detection Confidence Threshold",
            min_value=0.1,
            max_value=0.9,
            value=0.3,
            step=0.1,
            help="Minimum confidence required for emotion detection"
        )
        
        songs_per_recommendation = st.selectbox(
            "Songs per recommendation",
            options=[5, 10, 15, 20],
            index=1
        )
    
    with col2:
        enable_notifications = st.checkbox("Enable notifications", value=True)
        
        auto_play_previews = st.checkbox("Auto-play song previews", value=False)
    
    if st.button("Save Preferences"):
        # In a full implementation, save these to user preferences
        st.success("Preferences saved!")
    
    st.markdown("---")
    
    # Data management
    st.write("### Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export My Data"):
            # Export user data as JSON
            emotion_history = db_manager.get_user_emotion_history(st.session_state.user_id, days=365)
            song_history = db_manager.get_user_song_history(st.session_state.user_id, limit=1000)
            
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
                ],
                'song_history': [
                    {
                        'title': entry.title,
                        'artist': entry.artist,
                        'emotion': entry.emotion,
                        'liked': entry.liked,
                        'played_at': entry.played_at.isoformat()
                    } for entry in song_history
                ]
            }
            
            import json
            json_data = json.dumps(export_data, indent=2)
            
            st.download_button(
                label="Download Data",
                data=json_data,
                file_name=f"emosound_data_{current_user.username}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("Clear History", type="secondary"):
            if st.confirm("Are you sure you want to clear all your history? This cannot be undone."):
                # Clear user history
                session = db_manager.get_session()
                session.query(db_manager.EmotionLog).filter(
                    db_manager.EmotionLog.user_id == st.session_state.user_id
                ).delete()
                session.query(db_manager.UserSongHistory).filter(
                    db_manager.UserSongHistory.user_id == st.session_state.user_id
                ).delete()
                session.commit()
                
                st.success("History cleared!")
                st.rerun()
    
    with col3:
        if st.button("Delete Account", type="secondary"):
            st.error("⚠️ This will permanently delete your account and all data!")
            
            confirm_delete = st.text_input("Type 'DELETE' to confirm:")
            
            if confirm_delete == "DELETE":
                if st.button("Confirm Deletion", type="secondary"):
                    # Delete user and all associated data
                    session = db_manager.get_session()
                    
                    # Delete related records first
                    session.query(db_manager.EmotionLog).filter(
                        db_manager.EmotionLog.user_id == st.session_state.user_id
                    ).delete()
                    
                    session.query(db_manager.UserSongHistory).filter(
                        db_manager.UserSongHistory.user_id == st.session_state.user_id
                    ).delete()
                    
                    # Delete user
                    session.query(db_manager.User).filter(
                        db_manager.User.id == st.session_state.user_id
                    ).delete()
                    
                    session.commit()
                    session.close()
                    
                    # Logout user
                    auth_manager.logout()
                    st.success("Account deleted successfully. You have been logged out.")
                    st.rerun()
    
    st.markdown("---")
    
    # Logout
    if st.button("Logout", type="primary"):
        auth_manager.logout()
        st.success("You have been logged out.")
        st.rerun()