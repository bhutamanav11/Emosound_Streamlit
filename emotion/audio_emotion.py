import speech_recognition as sr
import streamlit as st
import io
import numpy as np
import wave
import logging
from emotion.text_emotion import text_emotion_detector

logger = logging.getLogger(__name__)

class AudioEmotionDetector:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Configure recognizer for better performance
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.operation_timeout = None
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.8
    
    def detect_emotion_from_webrtc_audio(self, audio_data, sample_rate=48000):
        """Detect emotion from WebRTC audio data"""
        try:
            # Convert numpy array to WAV bytes
            wav_bytes = self._numpy_to_wav(audio_data, sample_rate)
            
            # Convert to text using speech recognition
            text = self._audio_bytes_to_text(wav_bytes)
            
            if text:
                # Use text emotion detection
                emotion, confidence = text_emotion_detector.detect_emotion(text)
                logger.info(f"WebRTC Audio -> Text: '{text}' -> Emotion: {emotion}")
                return emotion, confidence, text
            else:
                return None, 0.0, None
                
        except Exception as e:
            logger.error(f"Error detecting emotion from WebRTC audio: {e}")
            return None, 0.0, None
    
    def detect_emotion_from_audio_file(self, uploaded_file):
        """Detect emotion from uploaded audio file"""
        try:
            # Read file content
            file_content = uploaded_file.read()
            
            # Convert to text
            text = self._file_content_to_text(file_content, uploaded_file.type)
            
            if text:
                # Use text emotion detection
                emotion, confidence = text_emotion_detector.detect_emotion(text)
                logger.info(f"Audio File -> Text: '{text}' -> Emotion: {emotion}")
                return emotion, confidence, text
            else:
                return None, 0.0, None
                
        except Exception as e:
            logger.error(f"Error detecting emotion from audio file: {e}")
            return None, 0.0, None
    
    def detect_emotion_from_simple_recorder(self, wav_audio_data):
        """Detect emotion from st_audiorec data"""
        try:
            if wav_audio_data is None:
                return None, 0.0, None
            
            # Convert to text
            text = self._audio_bytes_to_text(wav_audio_data)
            
            if text:
                # Use text emotion detection
                emotion, confidence = text_emotion_detector.detect_emotion(text)
                logger.info(f"Simple Recorder -> Text: '{text}' -> Emotion: {emotion}")
                return emotion, confidence, text
            else:
                return None, 0.0, None
                
        except Exception as e:
            logger.error(f"Error detecting emotion from simple recorder: {e}")
            return None, 0.0, None
    
    def _numpy_to_wav(self, audio_data, sample_rate=48000):
        """Convert numpy audio data to WAV bytes"""
        # Ensure mono audio
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
        
        # Normalize and convert to int16
        if audio_data.dtype != np.int16:
            # Normalize to [-1, 1] range first
            audio_data = audio_data.astype(np.float32)
            if np.max(np.abs(audio_data)) > 0:
                audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Convert to int16
            audio_data = np.int16(audio_data * 32767)
        
        # Create WAV file in memory
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def _audio_bytes_to_text(self, audio_bytes):
        """Convert audio bytes to text using speech recognition"""
        try:
            # Create AudioFile from bytes
            audio_file = io.BytesIO(audio_bytes)
            
            with sr.AudioFile(audio_file) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Record the audio
                audio = self.recognizer.record(source)
            
            # Try Google Speech Recognition first
            try:
                text = self.recognizer.recognize_google(audio, language='en-US')
                return text
            except sr.UnknownValueError:
                logger.warning("Google Speech Recognition could not understand audio")
                
                # Fallback to offline recognition (if available)
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    return text
                except (sr.UnknownValueError, sr.RequestError):
                    logger.warning("Sphinx could not understand audio")
                    return None
                    
            except sr.RequestError as e:
                logger.error(f"Google Speech Recognition request failed: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error converting audio to text: {e}")
            return None
    
    def _file_content_to_text(self, file_content, file_type):
        """Convert uploaded file content to text"""
        try:
            # Create audio file object
            audio_file = io.BytesIO(file_content)
            
            # Handle different file types
            if file_type in ['audio/wav', 'audio/wave']:
                with sr.AudioFile(audio_file) as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.record(source)
            else:
                # For other formats, we might need additional processing
                # This is a simplified approach - in production, you'd use pydub
                logger.warning(f"File type {file_type} may not be fully supported")
                with sr.AudioFile(audio_file) as source:
                    audio = self.recognizer.record(source)
            
            # Convert to text
            text = self.recognizer.recognize_google(audio, language='en-US')
            return text
            
        except Exception as e:
            logger.error(f"Error converting file to text: {e}")
            return None
    
    def get_supported_formats(self):
        """Get list of supported audio formats"""
        return ['wav', 'flac', 'aiff']
    
    def validate_audio_file(self, uploaded_file, max_size_mb=10):
        """Validate uploaded audio file"""
        if not uploaded_file:
            return False, "No file provided"
        
        # Check file size
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return False, f"File too large ({file_size_mb:.1f}MB). Maximum size: {max_size_mb}MB"
        
        # Check file type
        supported_types = [
            'audio/wav', 'audio/wave', 'audio/flac', 
            'audio/mp3', 'audio/mpeg', 'audio/m4a',
            'audio/ogg', 'audio/webm'
        ]
        
        if uploaded_file.type not in supported_types:
            return False, f"Unsupported file type: {uploaded_file.type}"
        
        return True, "Valid audio file"

# Global instance
audio_emotion_detector = AudioEmotionDetector()