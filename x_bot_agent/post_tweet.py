"""
Tweet posting module with AI generation and rate limiting.
"""
import logging
from typing import Optional
from config import get_x_client, get_gemini_model, PROMPTS, RATE_LIMIT_THRESHOLD, RATE_LIMIT_MAX, LOG_FILE
from database import (
    init_db, get_post_count, increment_post_count, 
    has_posted_before, record_posted_tweet
)

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.ERROR)


def generate_tweet(topic: str) -> Optional[str]:
    """
    Generate a tweet using Gemini AI based on a topic.
    Returns the generated text or None on failure.
    """
    try:
        model = get_gemini_model()
        prompt = f"{PROMPTS['generate_tweet']} {topic}"
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            print("Error: AI returned empty response")
            return None
            
        generated_text = response.text.strip()
        
        # Clean up common issues
        generated_text = generated_text.strip('"\'')  # Remove wrapping quotes
        
        # Truncate if too long
        if len(generated_text) > 280:
            generated_text = generated_text[:277] + "..."
            
        return generated_text
        
    except Exception as e:
        error_msg = f"Error generating tweet: {e}"
        logging.error(error_msg)
        print(error_msg)
        return None


def post_tweet(message: str, require_approval: bool = True) -> Optional[dict]:
    """
    Post a tweet with the given message.
    
    Args:
        message: The tweet text to post
        require_approval: If True, asks for user confirmation before posting
        
    Returns:
        The API response object or None on failure
    """
    try:
        # Validate message
        if not message or len(message.strip()) == 0:
            print("❌ Error: Empty message cannot be posted")
            return None
            
        if len(message) > 280:
            print(f"❌ Error: Message exceeds 280 character limit ({len(message)} characters)")
            return None

        # Rate limit check
        current_count = get_post_count()
        if current_count >= RATE_LIMIT_MAX:
            print(f"🚫 Monthly post limit reached ({current_count}/{RATE_LIMIT_MAX}). Cannot post.")
            return None
        elif current_count >= RATE_LIMIT_THRESHOLD:
            print(f"⚠️  Approaching monthly post limit ({current_count}/{RATE_LIMIT_MAX}).")
            
        # Duplicate check
        if has_posted_before(message):
            print("⚠️  Similar content already posted before. Skipping to avoid duplicates.")
            return None
        
        # Human approval
        if require_approval:
            print("\n" + "="*60)
            print("📝 TWEET PREVIEW:")
            print("-"*60)
            print(message)
            print("-"*60)
            print(f"Length: {len(message)}/280 characters")
            print(f"Posts this month: {current_count}/{RATE_LIMIT_MAX}")
            print("="*60)
            
            response = input("\n✅ Post this tweet? (y/n): ").strip().lower()
            if response != 'y':
                print("❌ Tweet posting cancelled.")
                return None
                
        # Post the tweet
        client = get_x_client()
        response = client.create_tweet(text=message)
        tweet_id = response.data['id']
        
        print(f"✅ Successfully posted tweet!")
        print(f"🔗 https://x.com/i/web/status/{tweet_id}")
        
        # Update tracking
        increment_post_count()
        record_posted_tweet(message, tweet_id)
        
        return response
        
    except Exception as e:
        error_str = str(e)
        if "402" in error_str or "credits" in error_str.lower():
            print("\n❌ POSTING FAILED: X API requires paid credits.")
            print("💡 Explanation: New X Developer accounts must prepay $5 to enable posting.")
            print("\n📋 Here is your tweet to copy-paste manually:")
            print("-" * 60)
            print(message)
            print("-" * 60)
            return None
            
        error_msg = f"❌ Error posting tweet: {e}"
        logging.error(error_msg)
        print(error_msg)
        return None


def copilot_mode(topic: str):
    """
    Interactive mode: Generate AI tweet and ask for approval.
    """
    print(f"\n🤖 Generating tweet about: {topic}")
    print("-"*40)
    
    generated = generate_tweet(topic)
    if not generated:
        print("Failed to generate tweet.")
        return
        
    post_tweet(generated, require_approval=True)


if __name__ == "__main__":
    init_db()
    # Example: copilot mode
    topic = input("Enter a topic for your tweet: ")
    copilot_mode(topic)
