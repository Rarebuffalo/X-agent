"""
X Bot Agent - Main CLI Entry Point (Free Tier)

Usage:
    python main.py post "topic"          # Generate and post an AI tweet
    python main.py copilot "topic"       # Generate tweet with approval (recommended)
    python main.py stats                 # Show bot statistics
"""
import argparse
import sys
from database import init_db, get_bot_stats
from post_tweet import post_tweet, generate_tweet, copilot_mode
from config import RATE_LIMIT_MAX


def show_banner():
    """Display the bot banner."""
    print("""
╔═══════════════════════════════════════════════════════════╗
║       🤖 X Bot Agent - AI-Powered Twitter Bot (Free)       ║
╠═══════════════════════════════════════════════════════════╣
║  Commands:                                                 ║
║    copilot <topic>  - Generate tweet with approval         ║
║    post <topic>     - Post AI-generated tweet (auto)       ║
║    stats            - Show statistics                      ║
╚═══════════════════════════════════════════════════════════╝
    """)


def cmd_post(args):
    """Handle post command."""
    topic = ' '.join(args.topic)
    print(f"\n🤖 Generating tweet about: {topic}")
    
    generated = generate_tweet(topic)
    if not generated:
        print("❌ Failed to generate tweet")
        return 1
    
    # If --auto flag, skip approval
    require_approval = not args.auto
    result = post_tweet(generated, require_approval=require_approval)
    
    return 0 if result else 1


def cmd_copilot(args):
    """Handle copilot command (always requires approval)."""
    topic = ' '.join(args.topic)
    copilot_mode(topic)
    return 0


def cmd_stats(args):
    """Handle stats command."""
    stats = get_bot_stats()
    
    print("\n📊 Bot Statistics")
    print("="*40)
    print(f"📝 Posts this month:      {stats['current_month_posts']}/{RATE_LIMIT_MAX}")
    print(f"📨 Total tweets posted:   {stats['total_tweets']}")
    print("="*40)
    
    # Rate limit warning
    remaining = RATE_LIMIT_MAX - stats['current_month_posts']
    if remaining < 50:
        print(f"⚠️  Warning: Only {remaining} posts remaining this month!")
    else:
        print(f"✅ {remaining} posts remaining this month")
    
    return 0


def main():
    """Main entry point."""
    # Initialize database
    init_db()
    
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="X Bot Agent - AI-Powered Twitter Bot (Free Tier)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py copilot "debugging React hooks"
  python main.py copilot "the future of AI"  
  python main.py post "Python tips" --auto
  python main.py stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Copilot command (primary)
    copilot_parser = subparsers.add_parser('copilot', help='Generate tweet with approval (recommended)')
    copilot_parser.add_argument('topic', nargs='+', help='Topic for the tweet')
    copilot_parser.set_defaults(func=cmd_copilot)
    
    # Post command
    post_parser = subparsers.add_parser('post', help='Post an AI-generated tweet')
    post_parser.add_argument('topic', nargs='+', help='Topic for the tweet')
    post_parser.add_argument('--auto', action='store_true', help='Skip approval prompt')
    post_parser.set_defaults(func=cmd_post)
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show bot statistics')
    stats_parser.set_defaults(func=cmd_stats)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show banner if no command
    if not args.command:
        show_banner()
        parser.print_help()
        return 0
    
    # Execute command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
