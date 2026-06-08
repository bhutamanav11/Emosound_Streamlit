# EmoSound

EmoSound is an AI-powered music recommendation platform that detects user emotions from text and voice input and recommends music that matches the detected mood. The system combines transformer-based emotion classification with Spotify audio feature analysis to deliver personalized recommendations in real time.

## Features

### Emotion Detection

* Emotion classification from text using DistilRoBERTa
* Voice-based emotion detection through speech-to-text processing
* Support for audio file uploads
* Confidence score for every prediction
* Multiple emotion categories including happy, sad, angry, excited, calm, anxious, romantic, energetic, melancholic, and confident

### Music Recommendation Engine

* Spotify Web API integration
* Audio feature matching using valence, energy, danceability, tempo, and acousticness
* Hybrid recommendation system combining content-based filtering, collaborative filtering, popularity metrics, and user preferences
* Real-time preference adaptation through user feedback

### User Management

* Secure authentication with password hashing
* Spotify OAuth integration
* Listening history and mood tracking
* Interactive analytics dashboard

## Technology Stack

| Component          | Technology         |
| ------------------ | ------------------ |
| Frontend           | Streamlit          |
| Backend            | Python             |
| NLP Model          | DistilRoBERTa      |
| Speech Recognition | Google Speech API  |
| Audio Processing   | Librosa            |
| Music Service      | Spotify Web API    |
| Database           | SQLite, SQLAlchemy |
| Visualization      | Plotly             |
| Authentication     | Bcrypt             |

## System Architecture

User Input (Text / Voice)

↓

Emotion Detection Model

↓

Emotion Classification

↓

Spotify Audio Feature Matching

↓

Recommendation Ranking

↓

Personalized Music Suggestions

## Performance

| Metric                          | Result      |
| ------------------------------- | ----------- |
| Emotion Classification Accuracy | 89%         |
| Average Response Time           | 1.2 seconds |
| Recommendation Relevance        | 78%         |
| Model Load Time                 | 3.5 seconds |

## Installation

```bash
git clone https://github.com/bhutamanav11/EmoSound_Streamlit_Version.git

cd EmoSound_Streamlit_Version

pip install -r requirements.txt
```

Create a `.env` file:

```env
DATABASE_URL=sqlite:///emosound.db

SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret

SECRET_KEY=your_secret_key
```

Initialize the database:

```bash
python database/init_db.py
```

Run the application:

```bash
streamlit run app.py
```

## Project Structure

```text
emosound/
│
├── app.py
├── requirements.txt
│
├── auth/
├── database/
├── emotion/
├── api/
├── ui/
└── utils/
```

## Future Improvements

* Real-time emotion recognition from live voice streams
* Deep learning based collaborative recommendation engine
* Playlist generation based on mood transitions
* Multi-language emotion detection
* Mobile application support

## Authors

Manav Bhuta & 
Aaryan Lunis

## License

This project is licensed under the MIT License.
