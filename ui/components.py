import streamlit as st
from datetime import datetime
import base64
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import requests
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def render_app_header():
    """Render the main application header"""
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 300;">
            🎵 EmoSound
        </h1>
        <p style="color: rgba(255, 255, 255, 0.8); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            Discover music that matches your emotions
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_emotion_display(emotion, confidence, color_code):
    """Render emotion detection results"""
    intensity = map_confidence_to_intensity(confidence)
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {color_code} 0%, {color_code}80 100%); 
                border-radius: 20px; padding: 2rem; margin: 1rem 0; text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h2 style="margin: 0; font-size: 2.5rem; text-transform: capitalize; color: white; 
                   text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
            😊 {emotion.title()}
        </h2>
        <div style="font-size: 1.3rem; margin-top: 0.5rem; color: rgba(255, 255, 255, 0.9);">
            Confidence: {confidence:.1%} ({intensity})
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_song_card_with_spotify_player(song, emotion_color, user_id, on_like=None, on_dislike=None, show_actions=True, card_index=0):
    """Render song card with embedded Spotify player"""
    
    # Generate unique keys
    timestamp = int(time.time() * 1000)
    song_id = song.get('spotify_id', 'unknown')
    unique_suffix = f"{card_index}_{timestamp}_{hash(str(song))}"
    base_key = f"song_{song_id}_{user_id}_{unique_suffix}"
    
    # Create container with styling
    st.markdown(f"""
    <div style="background: white; border-radius: 15px; padding: 1.5rem; margin: 1rem 0;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); border-left: 5px solid {emotion_color};">
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Album artwork
        if song.get('album_image'):
            try:
                st.image(song['album_image'], width=150)
            except:
                st.markdown("🎵", unsafe_allow_html=True)
        else:
            st.markdown("🎵", unsafe_allow_html=True)
    
    with col2:
        # Song info
        song_title = song.get('title', 'Unknown Title')
        song_artist = song.get('artist', 'Unknown Artist')
        song_album = song.get('album', 'Unknown Album')
        
        st.markdown(f"""
        <div style="font-size: 1.4rem; font-weight: 700; color: #2c3e50; margin-bottom: 0.3rem;">
            {song_title}
        </div>
        <div style="font-size: 1.1rem; color: #7f8c8d; margin-bottom: 0.3rem;">
            {song_artist}
        </div>
        <div style="font-size: 0.9rem; color: #95a5a6; margin-bottom: 1rem;">
            {song_album}
        </div>
        """, unsafe_allow_html=True)
        
        # Spotify embed player
        if song.get('spotify_id'):
            embed_url = f"https://open.spotify.com/embed/track/{song['spotify_id']}?utm_source=generator&theme=0"
            
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
        elif song.get('preview_url'):
            # Fallback to HTML5 audio if no Spotify ID
            st.audio(song['preview_url'], key=f"audio_{base_key}")
        
        # Action buttons
        if show_actions:
            col_like, col_dislike, col_open, col_save = st.columns(4)
            
            with col_like:
                if st.button("👍 Like", key=f"like_{base_key}", use_container_width=True):
                    if on_like:
                        on_like(song)
                    st.success("Liked! ❤️")
            
            with col_dislike:
                if st.button("👎 Skip", key=f"dislike_{base_key}", use_container_width=True):
                    if on_dislike:
                        on_dislike(song)
                    st.info("Skipped!")
            
            with col_open:
                if song.get('external_url'):
                    st.markdown(f"""
                    <a href="{song['external_url']}" target="_blank" style="
                        display: inline-block; 
                        background: #1DB954; 
                        color: white; 
                        padding: 0.5rem 1rem; 
                        border-radius: 20px; 
                        text-decoration: none;
                        text-align: center;
                        font-size: 0.9rem;
                        font-weight: 600;
                        width: 100%;
                    ">🎧 Open Spotify</a>
                    """, unsafe_allow_html=True)
            
            with col_save:
                if st.button("➕ Save", key=f"save_{base_key}", use_container_width=True):
                    st.info("Saved to favorites!")
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")

# Keep the old function for backward compatibility
def render_song_card(song, emotion_color, user_id, on_like=None, on_dislike=None, show_actions=True, card_index=0):
    """Alias for the Spotify player version"""
    render_song_card_with_spotify_player(song, emotion_color, user_id, on_like, on_dislike, show_actions, card_index)

def render_quote_card(quote_data):
    """Render motivational quote card"""
    if quote_data:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); 
                    border-radius: 15px; padding: 2rem; margin: 1.5rem 0; 
                    border-left: 5px solid #3498db;">
            <div style="font-size: 1.3rem; font-style: italic; color: #2c3e50; 
                       margin-bottom: 1rem; line-height: 1.6;">
                "{quote_data['text']}"
            </div>
            <div style="font-size: 1rem; color: #7f8c8d; text-align: right; font-weight: 500;">
                — {quote_data['author']}
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_input_section():
    """Render emotion input section with multiple input types"""
    st.subheader("🎭 How are you feeling?")
    
    # Input type selection
    input_type = st.radio(
        "Choose input method:",
        ["Text Input", "Audio File Upload"],
        horizontal=True,
        key="input_type_selector"
    )
    
    emotion_data = None
    
    if input_type == "Text Input":
        text_input = st.text_area(
            "Describe how you're feeling:",
            placeholder="I'm feeling happy today because...",
            height=100,
            key="emotion_text_input"
        )
        
        if st.button("🎯 Analyze Text", type="primary", key="analyze_text_btn"):
            if text_input.strip():
                try:
                    # Try ML emotion detection first
                    try:
                        from emotion.text_emotion import ml_text_emotion_detector
                        with st.spinner("🤖 AI is analyzing your emotions..."):
                            emotion, confidence = ml_text_emotion_detector.detect_emotion(text_input)
                        
                        if emotion:
                            emotion_data = {
                                'emotion': emotion,
                                'confidence': confidence,
                                'input_type': 'ml_text',
                                'input_text': text_input
                            }
                            st.success(f"✨ Detected emotion: **{emotion}** (confidence: {confidence:.1%})")
                        else:
                            emotion_data = simple_emotion_detection(text_input)
                    except Exception as e:
                        logger.warning(f"ML detection failed, using fallback: {e}")
                        emotion_data = simple_emotion_detection(text_input)
                        
                except Exception as e:
                    st.error(f"Error analyzing text: {str(e)}")
            else:
                st.warning("Please enter some text to analyze")
    
    elif input_type == "Audio File Upload":
        st.markdown("""
        <div style="background: #f8f9fa; border-radius: 10px; padding: 1.5rem; 
                    margin: 1rem 0; border: 2px dashed #dee2e6; text-align: center;">
            <h4>📁 Upload Audio File</h4>
            <p>Upload an audio file (wav, mp3, m4a) to analyze emotion</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=['wav', 'mp3', 'm4a', 'flac'],
            help="Upload audio file (max 10MB)",
            key="audio_file_uploader"
        )
        
        if uploaded_file and st.button("🎯 Analyze Audio File", type="primary", key="analyze_audio_btn"):
            with st.spinner("🎙️ Processing audio..."):
                try:
                    from emotion.audio_emotion import ml_audio_emotion_detector
                    emotion, confidence, text = ml_audio_emotion_detector.detect_emotion_from_audio_file(uploaded_file)
                    
                    if emotion:
                        emotion_data = {
                            'emotion': emotion,
                            'confidence': confidence,
                            'input_type': 'ml_audio',
                            'input_text': text
                        }
                        st.success(f"✨ Detected emotion: **{emotion}** (confidence: {confidence:.1%})")
                        if text:
                            st.info(f"📝 Transcribed: '{text}'")
                    else:
                        st.error("Could not detect emotion from audio file")
                        
                except Exception as e:
                    logger.warning(f"ML audio detection failed: {e}")
                    st.error("Could not process audio file. Please ensure it's a valid audio format.")
    
    return emotion_data

def simple_emotion_detection(text):
    """Simple fallback emotion detection"""
    emotion_keywords = {
        'happy': ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'good', 'fantastic', 'awesome', 'love'],
        'sad': ['sad', 'down', 'depressed', 'unhappy', 'blue', 'melancholy', 'disappointed', 'hurt', 'crying'],
        'angry': ['angry', 'mad', 'furious', 'irritated', 'annoyed', 'rage', 'hate', 'frustrated', 'pissed'],
        'excited': ['excited', 'thrilled', 'pumped', 'energized', 'enthusiastic', 'eager', 'stoked'],
        'calm': ['calm', 'peaceful', 'relaxed', 'serene', 'tranquil', 'zen', 'composed', 'chill'],
        'anxious': ['anxious', 'nervous', 'worried', 'stressed', 'tense', 'afraid', 'scared', 'panicked'],
        'romantic': ['love', 'romantic', 'affection', 'adore', 'crush', 'heart', 'passion', 'loving'],
        'confident': ['confident', 'sure', 'certain', 'strong', 'proud', 'bold', 'empowered', 'determined']
    }
    
    text_lower = text.lower()
    scores = {}
    
    for emotion, keywords in emotion_keywords.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            scores[emotion] = score / len(keywords)
    
    if scores:
        best_emotion = max(scores, key=scores.get)
        confidence = min(scores[best_emotion] * 0.8, 0.9)
        st.info("💡 Using keyword-based detection")
        return {
            'emotion': best_emotion,
            'confidence': confidence,
            'input_type': 'simple_text',
            'input_text': text
        }
    
    return {
        'emotion': 'neutral',
        'confidence': 0.5,
        'input_type': 'simple_text',
        'input_text': text
    }

def render_emotion_history_chart(emotion_history):
    """Render emotion history visualization"""
    if not emotion_history:
        st.info("No emotion history available yet.")
        return
    
    try:
        # Prepare data
        dates = [entry.detected_at.date() if hasattr(entry, 'detected_at') else datetime.now().date() for entry in emotion_history]
        emotions = [entry.name if hasattr(entry, 'name') else str(entry) for entry in emotion_history]
        colors = [getattr(entry, 'color_code', '#667eea') for entry in emotion_history]
        
        # Create timeline chart
        fig = go.Figure()
        
        for i, (date, emotion, color) in enumerate(zip(dates, emotions, colors)):
            fig.add_trace(go.Scatter(
                x=[date],
                y=[emotion],
                mode='markers',
                marker=dict(size=15, color=color, line=dict(width=2, color='white')),
                name=emotion,
                showlegend=False,
                text=f"{emotion}<br>{date}",
                hoverinfo='text'
            ))
        
        fig.update_layout(
            title="Your Emotion Journey",
            xaxis_title="Date",
            yaxis_title="Emotion",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")

def render_mood_distribution_chart(emotion_history):
    """Render mood distribution pie chart"""
    if not emotion_history:
        return
    
    try:
        emotion_counts = {}
        emotion_colors = {}
        
        for entry in emotion_history:
            emotion_name = entry.name if hasattr(entry, 'name') else str(entry)
            if emotion_name not in emotion_counts:
                emotion_counts[emotion_name] = 0
                emotion_colors[emotion_name] = getattr(entry, 'color_code', '#667eea')
            emotion_counts[emotion_name] += 1
        
        if emotion_counts:
            fig = go.Figure(data=[go.Pie(
                labels=list(emotion_counts.keys()),
                values=list(emotion_counts.values()),
                marker_colors=[emotion_colors[emotion] for emotion in emotion_counts.keys()],
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
            )])
            
            fig.update_layout(title="Mood Distribution", height=400, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")

def render_spotify_connection_status(is_connected):
    """Render Spotify connection status"""
    if is_connected:
        st.success("✅ Connected to Spotify - Getting personalized recommendations!")
    else:
        st.info("🎵 Connect to Spotify for personalized recommendations and direct playback")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            **Benefits of connecting:**
            - 🎧 Play songs directly in the app
            - 🎵 Get personalized recommendations
            - 📊 See your Spotify playlists
            - 💾 Save songs to your library
            """)
        
        with col2:
            if st.button("🎧 Connect to Spotify", type="primary", key="spotify_connect_btn"):
                try:
                    from api.spotify_api import spotify_manager
                    auth_url = spotify_manager.get_auth_url()
                    if auth_url:
                        st.markdown(f'<meta http-equiv="refresh" content="0;url={auth_url}">', unsafe_allow_html=True)
                        st.info("Redirecting to Spotify...")
                    else:
                        st.error("Unable to generate Spotify authorization URL")
                except Exception as e:
                    st.error(f"Error connecting to Spotify: {str(e)}")

def render_user_stats(user_id):
    """Render user statistics dashboard"""
    try:
        from database.database import db_manager
        
        emotion_history = db_manager.get_user_emotion_history(user_id, days=30)
        song_history = db_manager.get_user_song_history(user_id, limit=100)
        
        col1, col2, col3, col4 = st.columns(4)
        
        stats = [
            ("Emotions Detected", len(emotion_history) if emotion_history else 0, "🎭"),
            ("Songs Played", len(song_history) if song_history else 0, "🎵"),
            ("Songs Liked", len([s for s in song_history if hasattr(s, 'liked') and s.liked == True]) if song_history else 0, "❤️"),
            ("Unique Emotions", len(set([getattr(entry, 'name', str(entry)) for entry in emotion_history])) if emotion_history else 0, "🌈")
        ]
        
        for col, (label, value, icon) in zip([col1, col2, col3, col4], stats):
            with col:
                st.markdown(f"""
                <div style="background: white; padding: 1.5rem; border-radius: 10px; 
                            text-align: center; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
                    <div style="font-size: 2.5rem;">{icon}</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #667eea; margin: 0.5rem 0;">
                        {value}
                    </div>
                    <div style="font-size: 1rem; color: #7f8c8d;">
                        {label}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error rendering stats: {str(e)}")

def map_confidence_to_intensity(confidence):
    """Map confidence score to intensity level"""
    if confidence >= 0.8:
        return "Very High"
    elif confidence >= 0.6:
        return "High"
    elif confidence >= 0.4:
        return "Medium"
    elif confidence >= 0.2:
        return "Low"
    else:
        return "Very Low"

def get_emotion_color(emotion_name):
    """Get color code for emotion"""
    emotion_colors = {
        'happy': '#FFD700',
        'sad': '#4169E1',
        'angry': '#FF4500',
        'excited': '#FF69B4',
        'calm': '#98FB98',
        'anxious': '#DDA0DD',
        'romantic': '#FF1493',
        'energetic': '#FF8C00',
        'melancholic': '#708090',
        'confident': '#DC143C',
        'neutral': '#808080'
    }
    return emotion_colors.get(emotion_name.lower(), '#667eea')

def format_duration(duration_ms):
    """Format duration from milliseconds to mm:ss"""
    if not duration_ms:
        return "Unknown"
    
    seconds = duration_ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}"

# ADD THIS FUNCTION TO THE END OF ui/components.py

def render_spotify_embed(spotify_id):
    """
    Render Spotify embed player
    FIXED: Uses correct embed URL
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