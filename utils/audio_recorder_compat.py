# utils/audio_recorder_compat.py
"""
Audio Recorder Compatibility Layer
Provides a unified interface for different audio recording libraries
"""

import streamlit as st
import logging
from enum import Enum
from typing import Optional, Tuple, Any

logger = logging.getLogger(__name__)

class AudioRecorderType(Enum):
    WEBRTC = "webrtc"
    ST_AUDIOREC = "st_audiorec"
    FILE_UPLOAD = "file_upload"
    HTML_RECORDER = "html_recorder"

class AudioRecorderManager:
    """Manages different audio recording implementations"""
    
    def __init__(self):
        self.available_recorders = self._detect_available_recorders()
        self.preferred_recorder = self._get_preferred_recorder()
    
    def _detect_available_recorders(self) -> list:
        """Detect which audio recording libraries are available"""
        available = []
        
        # Check for streamlit-webrtc
        try:
            import streamlit_webrtc
            available.append(AudioRecorderType.WEBRTC)
            logger.info("streamlit-webrtc is available")
        except ImportError:
            logger.info("streamlit-webrtc not available")
        
        # Check for st_audiorec
        try:
            import st_audiorec
            available.append(AudioRecorderType.ST_AUDIOREC)
            logger.info("st_audiorec is available")
        except ImportError:
            logger.info("st_audiorec not available")
        
        # File upload is always available
        available.append(AudioRecorderType.FILE_UPLOAD)
        
        # HTML recorder is always available (uses browser APIs)
        available.append(AudioRecorderType.HTML_RECORDER)
        
        return available
    
    def _get_preferred_recorder(self) -> AudioRecorderType:
        """Get preferred recorder based on availability and reliability"""
        if AudioRecorderType.WEBRTC in self.available_recorders:
            return AudioRecorderType.WEBRTC
        elif AudioRecorderType.ST_AUDIOREC in self.available_recorders:
            return AudioRecorderType.ST_AUDIOREC
        elif AudioRecorderType.HTML_RECORDER in self.available_recorders:
            return AudioRecorderType.HTML_RECORDER
        else:
            return AudioRecorderType.FILE_UPLOAD
    
    def render_audio_recorder(self, key: str = "audio_recorder") -> Tuple[Optional[str], Optional[float], Optional[str]]:
        """
        Render audio recorder UI and return emotion detection results
        Returns: (emotion, confidence, transcribed_text)
        """
        
        # Let user choose recorder type if multiple available
        if len(self.available_recorders) > 2:  # More than just file upload and HTML
            recorder_options = []
            recorder_labels = {
                AudioRecorderType.WEBRTC: "🎙️ WebRTC (Advanced)",
                AudioRecorderType.ST_AUDIOREC: "🎤 Simple Recorder",
                AudioRecorderType.FILE_UPLOAD: "📁 File Upload",
                AudioRecorderType.HTML_RECORDER: "🌐 Browser Recorder"
            }
            
            for recorder_type in self.available_recorders:
                if recorder_type in recorder_labels:
                    recorder_options.append(recorder_labels[recorder_type])
            
            selected_label = st.selectbox(
                "Choose recording method:",
                recorder_options,
                key=f"{key}_type_selector"
            )
            
            # Map back to enum
            label_to_type = {v: k for k, v in recorder_labels.items()}
            selected_type = label_to_type[selected_label]
        else:
            selected_type = self.preferred_recorder
        
        # Render the selected recorder
        if selected_type == AudioRecorderType.WEBRTC:
            return self._render_webrtc_recorder(key)
        elif selected_type == AudioRecorderType.ST_AUDIOREC:
            return self._render_st_audiorec(key)
        elif selected_type == AudioRecorderType.HTML_RECORDER:
            return self._render_html_recorder(key)
        else:  # FILE_UPLOAD
            return self._render_file_upload(key)
    
    def _render_webrtc_recorder(self, key: str) -> Tuple[Optional[str], Optional[float], Optional[str]]:
        """Render WebRTC audio recorder"""
        try:
            from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
            import av
            import numpy as np
            from collections import deque
            import threading
            
            # Initialize recorder in session state
            recorder_key = f"{key}_webrtc_recorder"
            if recorder_key not in st.session_state:
                st.session_state[recorder_key] = WebRTCAudioRecorder()
            
            recorder = st.session_state[recorder_key]
            
            # WebRTC configuration
            rtc_config = RTCConfiguration({
                "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
            })
            
            # WebRTC streamer
            webrtc_ctx = webrtc_streamer(
                key=f"{key}_webrtc_stream",
                mode=WebRtcMode.SENDONLY,
                audio_frame_callback=recorder.audio_frame_callback,
                rtc_configuration=rtc_config,
                media_stream_constraints={
                    "audio": {
                        "sampleRate": 48000,
                        "channelCount": 1,
                        "echoCancellation": True,
                        "noiseSuppression": True,
                    },
                    "video": False,
                },
                async_processing=True,
            )
            
            # Controls
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🎙️ Start Recording", 
                           disabled=not webrtc_ctx.state.playing,
                           key=f"{key}_start"):
                    recorder.start_recording()
                    st.success("Recording started!")
            
            with col2:
                if st.button("⏹️ Stop & Analyze", key=f"{key}_stop"):
                    with st.spinner("Processing audio..."):
                        return recorder.stop_and_analyze()
            
            # Status
            if webrtc_ctx.state.playing:
                st.info("🟢 Microphone active - Ready to record")
            else:
                st.warning("Click 'START' to activate microphone")
            
            return None, None, None
            
        except Exception as e:
            logger.error(f"WebRTC recorder error: {e}")
            st.error("WebRTC recorder not available. Falling back to file upload.")
            return self._render_file_upload(key)
    
    def _render_st_audiorec(self, key: str) -> Tuple[Optional[str], Optional[float], Optional[str]]:
        """Render st_audiorec recorder"""
        try:
            from st_audiorec import st_audiorec
            from emotion.audio_emotion import audio_emotion_detector
            
            st.info("🎤 Click the microphone button to start/stop recording")
            
            wav_audio_data = st_audiorec(key=f"{key}_audiorec")
            
            if wav_audio_data is not None:
                st.success("✅ Audio recorded!")
                
                # Show audio player
                st.audio(wav_audio_data, format='audio/wav')
                
                # Analyze button
                if st.button("🎯 Analyze Emotion", key=f"{key}_analyze"):
                    with st.spinner("Analyzing emotion..."):
                        emotion, confidence, text = audio_emotion_detector.detect_emotion_from_simple_recorder(wav_audio_data)
                        
                        if emotion:
                            st.success(f"Detected emotion: **{emotion}** (confidence: {confidence:.1%})")
                            if text:
                                st.info(f"Transcribed: '{text}'")
                            return emotion, confidence, text
                        else:
                            st.error("Could not detect emotion from audio")
            
            return None, None, None
            
        except Exception as e:
            logger.error(f"st_audiorec error: {e}")
            st.error("Simple recorder not available. Falling back to file upload.")
            return self._render_file_upload(key)
    
    def _render_html_recorder(self, key: str) -> Tuple[Optional[str], Optional[float], Optional[str]]:
        """Render HTML/JavaScript recorder"""
        st.info("🌐 Browser-based audio recorder")
        st.components.v1.html(
            self._get_html_recorder_code(),
            height=300
        )
        
        # Check for completed recording (in a real implementation)
        if st.button("🔄 Check for Recording", key=f"{key}_check"):
            st.info("HTML recorder integration would be implemented here")
        
        return None, None, None
    
    def _render_file_upload(self, key: str) -> Tuple[Optional[str], Optional[float], Optional[str]]:
        """Render file upload interface"""
        from emotion.audio_emotion import audio_emotion_detector
        
        st.info("📁 Upload an audio file for emotion analysis")
        
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=['wav', 'mp3', 'm4a', 'flac', 'ogg'],
            key=f"{key}_upload",
            help="Upload audio file (max 10MB, WAV format recommended)"
        )
        
        if uploaded_file:
            # Validate file
            is_valid, message = audio_emotion_detector.validate_audio_file(uploaded_file)
            
            if not is_valid:
                st.error(message)
                return None, None, None
            
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Show file info
            st.write(f"**Size:** {uploaded_file.size:,} bytes")
            st.write(f"**Type:** {uploaded_file.type}")
            
            # Play uploaded audio
            st.audio(uploaded_file, format=uploaded_file.type)
            
            # Analyze button
            if st.button("🎯 Analyze Emotion", key=f"{key}_file_analyze"):
                with st.spinner("Processing audio file..."):
                    emotion, confidence, text = audio_emotion_detector.detect_emotion_from_audio_file(uploaded_file)
                    
                    if emotion:
                        st.success(f"Detected emotion: **{emotion}** (confidence: {confidence:.1%})")
                        if text:
                            st.info(f"Transcribed: '{text}'")
                        return emotion, confidence, text
                    else:
                        st.error("Could not detect emotion from audio file")
        
        return None, None, None
    
    def _get_html_recorder_code(self) -> str:
        """Get HTML/JavaScript code for browser-based recording"""
        return """
        <div style="text-align: center; padding: 20px;">
            <button onclick="toggleRecording()" id="recordBtn" 
                    style="background: #667eea; color: white; border: none; 
                           border-radius: 20px; padding: 15px 30px; font-size: 16px;">
                🎤 Start Recording
            </button>
            <div id="status" style="margin: 20px; color: #666;"></div>
            <div id="audioContainer" style="margin: 20px;"></div>
        </div>
        
        <script>
        let mediaRecorder;
        let isRecording = false;
        
        async function toggleRecording() {
            if (!isRecording) {
                await startRecording();
            } else {
                stopRecording();
            }
        }
        
        async function startRecording() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                
                mediaRecorder.start();
                isRecording = true;
                
                document.getElementById('recordBtn').textContent = '⏹️ Stop Recording';
                document.getElementById('status').textContent = '🔴 Recording...';
                
            } catch (error) {
                document.getElementById('status').textContent = '❌ Error accessing microphone';
            }
        }
        
        function stopRecording() {
            if (mediaRecorder) {
                mediaRecorder.stop();
                isRecording = false;
                
                document.getElementById('recordBtn').textContent = '🎤 Start Recording';
                document.getElementById('status').textContent = '✅ Recording completed';
            }
        }
        </script>
        """

class WebRTCAudioRecorder:
    """WebRTC-specific audio recorder implementation"""
    
    def __init__(self):
        from collections import deque
        import threading
        
        self.audio_frames = deque(maxlen=1000)
        self.is_recording = False
        self.lock = threading.Lock()
    
    def audio_frame_callback(self, frame):
        import av
        import numpy as np
        
        with self.lock:
            if self.is_recording:
                audio_array = frame.to_ndarray()
                self.audio_frames.append(audio_array)
        return frame
    
    def start_recording(self):
        with self.lock:
            self.is_recording = True
            self.audio_frames.clear()
    
    def stop_and_analyze(self):
        with self.lock:
            self.is_recording = False
            if self.audio_frames:
                import numpy as np
                from emotion.audio_emotion import audio_emotion_detector
                
                audio_data = np.concatenate(list(self.audio_frames), axis=0)
                return audio_emotion_detector.detect_emotion_from_webrtc_audio(audio_data)
        
        return None, 0.0, None

# Global instance