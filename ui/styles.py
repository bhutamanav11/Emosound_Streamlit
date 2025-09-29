def get_custom_css():
    """Return custom CSS for the application"""
    return """
    <style>
    /* Global Styles */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header Styles */
    .app-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .app-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 300;
    }
    
    .app-header p {
        color: rgba(255, 255, 255, 0.8);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    /* Emotion Card Styles */
    .emotion-card {
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .emotion-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .emotion-display {
        text-align: center;
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
    }
    
    .emotion-display h2 {
        margin: 0;
        font-size: 2rem;
        text-transform: capitalize;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .emotion-display .confidence {
        font-size: 1.2rem;
        margin-top: 0.5rem;
        color: rgba(255, 255, 255, 0.9);
    }
    
    /* Song Card Styles */
    .song-card {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        border-left: 5px solid #667eea;
    }
    
    .song-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    
    .song-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.25rem;
    }
    
    .song-artist {
        font-size: 1rem;
        color: #7f8c8d;
        margin-bottom: 1rem;
    }
    
    .song-actions {
        display: flex;
        gap: 0.5rem;
        justify-content: flex-start;
        align-items: center;
    }
    
    /* Quote Styles */
    .quote-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 2rem;
        margin: 1.5rem 0;
        border-left: 5px solid #3498db;
    }
    
    .quote-text {
        font-size: 1.3rem;
        font-style: italic;
        color: #2c3e50;
        margin-bottom: 1rem;
        line-height: 1.6;
    }
    
    .quote-author {
        font-size: 1rem;
        color: #7f8c8d;
        text-align: right;
        font-weight: 500;
    }
    
    /* Input Styles */
    .audio-input-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 2px dashed #dee2e6;
        text-align: center;
    }
    
    .audio-input-container:hover {
        border-color: #667eea;
        background: #f0f2ff;
    }
    
    /* Button Styles */
    .custom-button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
    }
    
    .custom-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
    }
    
    .like-button {
        background: linear-gradient(45deg, #56ab2f, #a8e6cf);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .dislike-button {
        background: linear-gradient(45deg, #ff6b6b, #ffa8a8);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    /* Profile Styles */
    .profile-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .profile-stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #7f8c8d;
        margin-top: 0.5rem;
    }
    
    /* History Styles */
    .history-item {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
    }
    
    .history-date {
        font-size: 0.9rem;
        color: #95a5a6;
        margin-bottom: 0.5rem;
    }
    
    .history-emotion {
        font-weight: 600;
        text-transform: capitalize;
        margin-bottom: 0.25rem;
    }
    
    /* Navigation Styles */
    .nav-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    /* Loading Styles */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Alert Styles */
    .alert {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .alert-success {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
    }
    
    .alert-error {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
    }
    
    .alert-warning {
        background-color: #fff3cd;
        border-color: #ffeaa7;
        color: #856404;
    }
    
    .alert-info {
        background-color: #d1ecf1;
        border-color: #bee5eb;
        color: #0c5460;
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .app-header h1 {
            font-size: 2rem;
        }
        
        .song-card {
            padding: 0.75rem;
        }
        
        .emotion-display {
            padding: 1.5rem;
        }
        
        .profile-stats {
            grid-template-columns: 1fr;
        }
    }
    
    /* Hide Streamlit Default Elements */
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    .css-1v0mbdj.ebxwdo61 {
        margin-top: -1rem;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }
    </style>
    """

def get_emotion_gradient_css(emotion_color):
    """Get CSS for emotion-based gradient"""
    return f"""
    <style>
    .emotion-gradient {{
        background: linear-gradient(135deg, {emotion_color} 0%, {emotion_color}80 100%);
    }}
    </style>
    """