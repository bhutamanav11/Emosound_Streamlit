from transformers import pipeline
import logging
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextEmotionDetector:
    def __init__(self):
        self.classifier = None
        self.emotion_mapping = {
            'joy': 'happy',
            'happiness': 'happy',
            'sadness': 'sad',
            'anger': 'angry',
            'fear': 'anxious',
            'surprise': 'excited',
            'love': 'romantic',
            'disgust': 'angry',
            'optimism': 'confident',
            'pessimism': 'sad'
        }
    
    @st.cache_resource
    def load_model(_self):
        """Load the emotion classification model"""
        try:
            _self.classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True
            )
            logger.info("Text emotion model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading text emotion model: {e}")
            return False
    
    def detect_emotion(self, text):
        """Detect emotion from text input"""
        if not self.classifier:
            if not self.load_model():
                return None, 0.0
        
        try:
            # Get predictions
            predictions = self.classifier(text)
            
            # Find the highest confidence prediction
            best_prediction = max(predictions[0], key=lambda x: x['score'])
            
            # Map to our emotion categories
            detected_emotion = best_prediction['label'].lower()
            confidence = best_prediction['score']
            
            # Map to our standardized emotions
            mapped_emotion = self.emotion_mapping.get(detected_emotion, detected_emotion)
            
            logger.info(f"Detected emotion: {mapped_emotion} (confidence: {confidence:.2f})")
            
            return mapped_emotion, confidence
            
        except Exception as e:
            logger.error(f"Error detecting emotion from text: {e}")
            return None, 0.0
    
    def get_emotion_breakdown(self, text):
        """Get detailed emotion breakdown with all scores"""
        if not self.classifier:
            if not self.load_model():
                return {}
        
        try:
            predictions = self.classifier(text)
            emotion_scores = {}
            
            for pred in predictions[0]:
                emotion = pred['label'].lower()
                mapped_emotion = self.emotion_mapping.get(emotion, emotion)
                emotion_scores[mapped_emotion] = pred['score']
            
            return emotion_scores
            
        except Exception as e:
            logger.error(f"Error getting emotion breakdown: {e}")
            return {}

# Global instance
text_emotion_detector = TextEmotionDetector()