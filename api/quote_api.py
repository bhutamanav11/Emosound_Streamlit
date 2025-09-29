import requests
import random
import logging
from config import config

logger = logging.getLogger(__name__)

class QuoteManager:
    def __init__(self):
        self.api_key = config.QUOTE_API_KEY
        self.api_url = config.QUOTE_API_URL
        
        # Fallback quotes for each emotion
        self.fallback_quotes = {
            'happy': [
                "Happiness is not something readymade. It comes from your own actions. - Dalai Lama",
                "The purpose of our lives is to be happy. - Dalai Lama",
                "Happiness is when what you think, what you say, and what you do are in harmony. - Mahatma Gandhi"
            ],
            'sad': [
                "The wound is the place where the Light enters you. - Rumi",
                "Tears are words that need to be written. - Paulo Coelho",
                "Every man has his secret sorrows which the world knows not. - Henry Wadsworth Longfellow"
            ],
            'angry': [
                "Anger is an acid that can do more harm to the vessel in which it is stored than to anything on which it is poured. - Mark Twain",
                "For every minute you remain angry, you give up sixty seconds of peace of mind. - Ralph Waldo Emerson",
                "Holding on to anger is like grasping a hot coal with the intent of throwing it at someone else. - Buddha"
            ],
            'excited': [
                "The way to get started is to quit talking and begin doing. - Walt Disney",
                "Life is what happens to you while you're busy making other plans. - John Lennon",
                "Enthusiasm is the mother of effort, and without it nothing great was ever achieved. - Ralph Waldo Emerson"
            ],
            'calm': [
                "Peace comes from within. Do not seek it without. - Buddha",
                "Calmness is the cradle of power. - Josiah Gilbert Holland",
                "In the midst of movement and chaos, keep stillness inside of you. - Deepak Chopra"
            ],
            'anxious': [
                "You have power over your mind - not outside events. Realize this, and you will find strength. - Marcus Aurelius",
                "Anxiety does not empty tomorrow of its sorrows, but only empties today of its strength. - Charles Spurgeon",
                "The present moment is the only time over which we have dominion. - Thich Nhat Hanh"
            ],
            'romantic': [
                "Love is composed of a single soul inhabiting two bodies. - Aristotle",
                "The best love is the kind that awakens the soul. - Nicholas Sparks",
                "Love is not about how many days, months, or years you have been together. Love is about how much you love each other every single day. - Unknown"
            ],
            'energetic': [
                "Energy and persistence conquer all things. - Benjamin Franklin",
                "The energy of the mind is the essence of life. - Aristotle",
                "Positive energy knows no boundaries. If everyone were to spread positive energy on the Internet, the world would be a much better place. - Lu Wei"
            ],
            'melancholic': [
                "There is a pleasure in the pathless woods, there is a rapture in the lonely shore. - Lord Byron",
                "Melancholy is the happiness of being sad. - Victor Hugo",
                "The good times of today are the sad thoughts of tomorrow. - Bob Marley"
            ],
            'confident': [
                "Confidence is the most beautiful thing you can possess. - Sabrina Carpenter",
                "With confidence, you have won before you have started. - Marcus Garvey",
                "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle. - Christian D. Larson"
            ]
        }
    
    def get_quote_for_emotion(self, emotion):
        """Get motivational quote based on emotion"""
        try:
            # First try API if available
            if self.api_key and self.api_url:
                quote = self._fetch_quote_from_api(emotion)
                if quote:
                    return quote
            
            # Fall back to predefined quotes
            emotion_quotes = self.fallback_quotes.get(emotion.lower(), self.fallback_quotes['happy'])
            selected_quote = random.choice(emotion_quotes)
            
            # Parse quote and author
            if ' - ' in selected_quote:
                text, author = selected_quote.rsplit(' - ', 1)
                return {
                    'text': text.strip(),
                    'author': author.strip(),
                    'emotion': emotion
                }
            else:
                return {
                    'text': selected_quote,
                    'author': 'Unknown',
                    'emotion': emotion
                }
                
        except Exception as e:
            logger.error(f"Error getting quote for emotion {emotion}: {e}")
            return {
                'text': "Every moment is a fresh beginning.",
                'author': 'T.S. Eliot',
                'emotion': emotion
            }
    
    def _fetch_quote_from_api(self, emotion):
        """Fetch quote from external API"""
        try:
            # Map emotions to API categories
            emotion_mapping = {
                'happy': 'happiness',
                'sad': 'sadness',
                'angry': 'anger',
                'excited': 'success',
                'calm': 'peace',
                'anxious': 'courage',
                'romantic': 'love',
                'energetic': 'motivational',
                'melancholic': 'life',
                'confident': 'confidence'
            }
            
            category = emotion_mapping.get(emotion.lower(), 'inspirational')
            
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            params = {
                'category': category,
                'count': 1
            }
            
            response = requests.get(
                self.api_url,
                headers=headers,
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and 'data' in data and data['data']:
                    quote_data = data['data'][0]
                    return {
                        'text': quote_data.get('quoteText', '').strip(),
                        'author': quote_data.get('quoteAuthor', 'Unknown').strip(),
                        'emotion': emotion
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching quote from API: {e}")
            return None
    
    def get_daily_quote(self):
        """Get a general inspirational quote for the day"""
        emotions = list(self.fallback_quotes.keys())
        random_emotion = random.choice(emotions)
        return self.get_quote_for_emotion(random_emotion)

# Global quote manager
quote_manager = QuoteManager()