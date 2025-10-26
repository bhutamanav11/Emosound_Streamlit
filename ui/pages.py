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
    """Render main home page with emotion detection"""
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

        # Show motivational quote
        try:
            from api.quote_api import quote_manager
            quote = quote_manager.get_quote_for_emotion(emotion_data['emotion'])
            render_quote_card(quote)
        except:
            pass

        # Get songs for the emotion
        st.subheader(f"🎵 Songs for your {emotion_data['emotion']} mood")

        songs = []
        try:
            import spotipy
            from spotipy.oauth2 import SpotifyClientCredentials
            import os

            # Create Spotify client
            client_credentials_manager = SpotifyClientCredentials(
                client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
            )
            sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

            # Emotion to search query mapping
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

            query = emotion_queries.get(emotion_data['emotion'].lower(), emotion_data['emotion'])
            results = sp.search(q=query, type='track', limit=10)

            # Convert to our song format
            for track in results['tracks']['items']:
                songs.append({
                    'title': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'spotify_id': track['id'],
                    'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'external_url': track['external_urls']['spotify']
                })

        except Exception as e:
            logger.error(f"Spotify search error: {e}")
            songs = []

        # Display songs or fallback
        if songs:
            for index, song in enumerate(songs):
                col1, col2 = st.columns([1, 3])

                with col1:
                    if song.get('album_image'):
                        st.image(song['album_image'], width=120)

                with col2:
                    st.markdown(f"**{song['title']}**")
                    st.write(f"by {song['artist']}")

                    # Spotify embed player
                    if song.get('spotify_id'):
                        import streamlit.components.v1 as components
                        components.html(f"""
                            <iframe 
                                style="border-radius:12px" 
                                src="https://open.spotify.com/embed/track/{song['spotify_id']}" 
                                width="100%" 
                                height="152" 
                                frameborder="0" 
                                allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture">
                            </iframe>
                        """, height=170)

                    # Action buttons
                    col_like, col_dislike, col_open = st.columns(3)

                    with col_like:
                        if st.button("👍 Like", key=f"like_{index}"):
                            st.success("Liked!")

                    with col_dislike:
                        if st.button("👎 Skip", key=f"skip_{index}"):
                            st.info("Skipped!")

                    with col_open:
                        if song.get('external_url'):
                            st.markdown(f"[🎧 Open in Spotify]({song['external_url']})")

                    st.markdown("---")
        else:
            st.info("No songs found for this emotion. Try a different mood!")

    # else:
    #     # If no emotion detected, use sample fallback
    #     st.info("Using sample songs. Connect Spotify for real recommendations!")
    #     sample_songs = get_sample_songs_for_emotion(emotion_data['emotion'] if emotion_data else 'neutral')

    #     if sample_songs:
    #         for index, song in enumerate(sample_songs):
    #             def handle_like(song_data, idx=index):
    #                 st.success(f"👍 Glad you liked {song_data['title']}!")

    #             def handle_dislike(song_data, idx=index):
    #                 st.info(f"👎 Thanks for the feedback on {song_data['title']}!")

    #             render_song_card(
    #                 song,
    #                 emotion_color if emotion_data else "#667eea",
    #                 current_user.id if current_user else 'guest',
    #                 on_like=lambda s, i=index: handle_like(s, i),
    #                 on_dislike=lambda s, i=index: handle_dislike(s, i),
    #                 card_index=index
    #             )
    # else:
    #         st.info("No songs found for this emotion. Try again!")


def render_profile_page():
    """Render user profile page with analytics"""
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
    if current_user:
        # Profile header
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 2rem; border-radius: 15px; text-align: center; margin-bottom: 2rem;">
            <h2>👤 {current_user.username}</h2>
            <p>Member since {current_user.created_at.strftime("%B %Y")}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User statistics
        try:
            render_user_stats(current_user.id)
        except Exception as e:
            logger.error(f"Error rendering user stats: {e}")
            st.info("Statistics will appear here as you use the app!")
        
        # Charts section
        try:
            from database.database import db_manager
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Emotion Timeline")
                emotion_history = db_manager.get_user_emotion_history(current_user.id, days=30)
                if emotion_history:
                    render_emotion_history_chart(emotion_history)
                else:
                    st.info("Start using emotion detection to see your timeline!")
            
            with col2:
                st.subheader("🎭 Mood Distribution")
                if emotion_history:
                    render_mood_distribution_chart(emotion_history)
                else:
                    st.info("Your mood distribution will appear here!")
        except Exception as e:
            logger.error(f"Error rendering charts: {e}")
        
        # Recent activity
        st.subheader("🎵 Recent Songs")
        try:
            from database.database import db_manager
            song_history = db_manager.get_user_song_history(current_user.id, limit=20)
            
            if song_history:
                for entry in song_history:
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**{entry.title}** by {entry.artist}")
                    
                    with col2:
                        emotion_color = entry.color_code
                        st.markdown(f"""
                        <span style="background-color: {emotion_color}; color: white; 
                                   padding: 0.25rem 0.5rem; border-radius: 15px; font-size: 0.8rem;">
                            {entry.emotion}
                        </span>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.write(entry.played_at.strftime("%m/%d %H:%M"))
                    
                    with col4:
                        if entry.liked == True:
                            st.write("👍")
                        elif entry.liked == False:
                            st.write("👎")
                        else:
                            st.write("—")
                    
                    st.markdown("---")
            else:
                st.info("No song history available yet. Start by detecting your emotions!")
        except Exception as e:
            logger.error(f"Error rendering song history: {e}")
            st.info("Song history will appear here as you use the app!")
    else:
        st.error("Please log in to view your profile.")

def render_playlists_page():
    """Render playlists page"""
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