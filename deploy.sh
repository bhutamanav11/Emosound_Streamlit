#!/bin/bash

# EmoSound Deployment Script

set -e

echo "🎵 Deploying EmoSound Application..."

# Check if required environment variables are set
required_vars=("SPOTIFY_CLIENT_ID" "SPOTIFY_CLIENT_SECRET" "SECRET_KEY")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var environment variable is not set"
        exit 1
    fi
done

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs models static/css static/images

# Set permissions
chmod 755 data logs
chmod 644 .env

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
python -c "from database.init_db import initialize_database; initialize_database()"

# Download required ML models (if needed)
echo "🤖 Checking ML models..."
python -c "
from emotion.text_emotion import text_emotion_detector
print('Loading text emotion model...')
text_emotion_detector.load_model()
print('✅ Model loaded successfully')
"

# Run tests (if available)
if [ -f "tests/test_app.py" ]; then
    echo "🧪 Running tests..."
    python -m pytest tests/ -v
fi

# Start application
echo "🚀 Starting EmoSound application..."
streamlit run app.py --server.port=8501 --server.address=0.0.0.0