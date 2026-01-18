"""
Centralized configuration for X Bot Agent.
Handles environment variables, API clients, and bot settings.
"""
import os
from dotenv import load_dotenv
import tweepy
import google.generativeai as genai

# Load environment variables
load_dotenv()

# =============================================================================
# X API Configuration
# =============================================================================
X_API_KEY = os.getenv('X_API_KEY')
X_API_SECRET_KEY = os.getenv('X_API_SECRET_KEY')
X_ACCESS_TOKEN = os.getenv('X_ACCESS_TOKEN')
X_ACCESS_TOKEN_SECRET = os.getenv('X_ACCESS_TOKEN_SECRET')

# Validate X API credentials
def validate_x_credentials():
    """Check if all X API credentials are present."""
    required = [X_API_KEY, X_API_SECRET_KEY, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET]
    if not all(required):
        missing = []
        if not X_API_KEY: missing.append('X_API_KEY')
        if not X_API_SECRET_KEY: missing.append('X_API_SECRET_KEY')
        if not X_ACCESS_TOKEN: missing.append('X_ACCESS_TOKEN')
        if not X_ACCESS_TOKEN_SECRET: missing.append('X_ACCESS_TOKEN_SECRET')
        raise ValueError(f"Missing X API credentials: {', '.join(missing)}")
    return True

# Initialize X API client
def get_x_client():
    """Get authenticated Tweepy client."""
    validate_x_credentials()
    return tweepy.Client(
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET_KEY,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True
    )

# =============================================================================
# Google Gemini Configuration
# =============================================================================
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = 'gemini-2.5-flash'  # Latest stable model

def validate_gemini_credentials():
    """Check if Gemini API key is present."""
    if not GEMINI_API_KEY:
        raise ValueError("Missing GEMINI_API_KEY in environment variables")
    return True

def get_gemini_model():
    """Get configured Gemini model."""
    validate_gemini_credentials()
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel(GEMINI_MODEL)

# =============================================================================
# Rate Limiting Configuration
# =============================================================================
RATE_LIMIT_THRESHOLD = int(os.getenv('RATE_LIMIT_THRESHOLD', 450))
RATE_LIMIT_MAX = int(os.getenv('RATE_LIMIT_MAX', 500))

# =============================================================================
# Database Configuration
# =============================================================================
DB_NAME = 'bot.db'  # Single consolidated database

# =============================================================================
# Bot Personality & Prompts
# =============================================================================
BOT_PERSONALITY = os.getenv('BOT_PERSONALITY', 'friendly and helpful developer assistant')

# System prompts for different bot actions
PROMPTS = {
    'reply': f"""You are a {BOT_PERSONALITY}. 
Read the following tweet and draft a supportive, engaging response.
Keep the response under 250 characters (to leave room for @mention).
Be genuine and avoid generic responses.
Do NOT use hashtags unless they're highly relevant.
Do NOT start with "I" - vary your response openers.

Tweet to reply to:""",

    'generate_tweet': f"""You are a {BOT_PERSONALITY} who tweets about tech, coding, and building in public.
Generate a single tweet based on the following topic or prompt.
Keep it under 280 characters.
Be authentic, insightful, and engaging.
Use emojis sparingly (max 1-2).
Do NOT use too many hashtags (max 1-2 if relevant).

Topic:""",

    'quote_retweet': f"""You are a {BOT_PERSONALITY}.
Create a brief quote for retweeting the following tweet.
Keep it under 100 characters.
Add genuine value or perspective.
Avoid generic praise like "Great post!" or "So true!".

Original tweet:"""
}

# =============================================================================
# Logging Configuration
# =============================================================================
LOG_FILE = 'bot_errors.log'
