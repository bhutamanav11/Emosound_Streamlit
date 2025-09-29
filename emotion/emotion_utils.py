import colorsys
from database.database import db_manager
import logging

logger = logging.getLogger(__name__)

class EmotionUtils:
    @staticmethod
    def get_emotion_color(emotion_name):
        """Get color code for emotion"""
        try:
            emotion = db_manager.get_emotion_by_name(emotion_name)
            if emotion:
                return emotion.color_code
            return "#808080"  # Default gray
        except Exception as e:
            logger.error(f"Error getting emotion color: {e}")
            return "#808080"
    
    @staticmethod
    def get_complementary_color(hex_color):
        """Get complementary color for better contrast"""
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            
            # Convert to RGB
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Convert to HSV
            hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
            
            # Get complementary hue
            comp_hue = (hsv[0] + 0.5) % 1.0
            
            # Convert back to RGB
            comp_rgb = colorsys.hsv_to_rgb(comp_hue, hsv[1], hsv[2])
            comp_rgb = tuple(int(c * 255) for c in comp_rgb)
            
            # Convert to hex
            return f"#{comp_rgb[0]:02x}{comp_rgb[1]:02x}{comp_rgb[2]:02x}"
            
        except Exception as e:
            logger.error(f"Error getting complementary color: {e}")
            return "#ffffff"
    
    @staticmethod
    def get_emotion_gradient(emotion_name):
        """Get CSS gradient for emotion"""
        base_color = EmotionUtils.get_emotion_color(emotion_name)
        comp_color = EmotionUtils.get_complementary_color(base_color)
        return f"linear-gradient(135deg, {base_color} 0%, {comp_color} 100%)"
    
    @staticmethod
    def validate_emotion_confidence(confidence, threshold=0.3):
        """Validate if emotion confidence is above threshold"""
        return confidence >= threshold
    
    @staticmethod
    def get_emotion_description(emotion_name):
        """Get description for emotion"""
        try:
            emotion = db_manager.get_emotion_by_name(emotion_name)
            if emotion:
                return emotion.description
            return "Unknown emotion"
        except Exception as e:
            logger.error(f"Error getting emotion description: {e}")
            return "Unknown emotion"
    
    @staticmethod
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

# Global instance
emotion_utils = EmotionUtils()