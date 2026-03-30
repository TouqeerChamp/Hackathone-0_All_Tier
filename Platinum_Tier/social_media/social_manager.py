#!/usr/bin/env python3
"""
Social Media Manager - Gold Tier Phase 2
=========================================
Agent Skill for social media automation across Facebook, Instagram, and Twitter.

This module provides mock API implementations that:
- Save posts to local JSON history files
- Log all actions to audit_logs
- Use graceful degradation for fault tolerance

Usage:
    from social_media.social_manager import (
        post_to_facebook,
        post_to_instagram,
        post_to_twitter,
        get_social_summary
    )

    # Post to Facebook
    post_to_facebook("Hello from our company!")

    # Post to Instagram with image
    post_to_instagram("images/post.jpg", "Beautiful day!")

    # Post to Twitter
    post_to_twitter("Tweet from our agent!")

    # Get 24h summary
    summary = get_social_summary()
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from graceful_degradation import with_graceful_degradation, FallbackMethod

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SocialMediaManager")

# Constants
SOCIAL_MEDIA_DIR = Path(__file__).parent
POST_HISTORY_FILE = SOCIAL_MEDIA_DIR / "post_history.json"
AUDIT_LOG_DIR = Path("logs/audit_logs")


class SocialMediaAuditLogger:
    """Audit logger for social media actions"""

    def __init__(self, log_dir: Path = AUDIT_LOG_DIR):
        self.log_dir = log_dir
        self._ensure_log_directory()
        self.log_file = self._get_daily_log_file()

    def _ensure_log_directory(self):
        """Create audit log directory if it doesn't exist"""
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _get_daily_log_file(self) -> Path:
        """Get today's audit log file path"""
        today = datetime.now().strftime("%Y%m%d")
        return self.log_dir / f"social_media_{today}.log"

    def log(self, action: str, platform: str, status: str, details: Dict[str, Any]):
        """
        Log a social media action in JSON Lines format

        Args:
            action: Type of action (e.g., 'post_created', 'summary_generated')
            platform: Social media platform (facebook, instagram, twitter)
            status: Action status ('success', 'error', 'degraded')
            details: Dictionary containing action details
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "platform": platform,
            "status": status,
            "details": details
        }

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            logger.info(f"[Audit] {platform}.{action} - {status}")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    def log_post_created(self, platform: str, post_id: str, content: Dict[str, Any]):
        """Log successful post creation"""
        self.log(
            action="post_created",
            platform=platform,
            status="success",
            details={
                "post_id": post_id,
                "content": content
            }
        )

    def log_post_failed(self, platform: str, error: str, content: Dict[str, Any]):
        """Log failed post creation"""
        self.log(
            action="post_creation_failed",
            platform=platform,
            status="error",
            details={
                "error": error,
                "content": content
            }
        )

    def log_summary_generated(self, posts_count: int, platforms: List[str]):
        """Log summary generation"""
        self.log(
            action="summary_generated",
            platform="all",
            status="success",
            details={
                "posts_count": posts_count,
                "platforms": platforms
            }
        )


# Initialize audit logger
audit_logger = SocialMediaAuditLogger()


def _generate_post_id(platform: str) -> str:
    """Generate a unique post ID for a platform"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{platform}_{timestamp}_{os.urandom(4).hex()}"


def _load_post_history() -> Dict[str, Any]:
    """Load post history from JSON file"""
    if not POST_HISTORY_FILE.exists():
        return {"posts": [], "metadata": {"created_at": datetime.now().isoformat()}}

    try:
        with open(POST_HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Failed to load post history: {e}")
        return {"posts": [], "metadata": {"created_at": datetime.now().isoformat()}}


def _save_post_history(history: Dict[str, Any]):
    """Save post history to JSON file"""
    try:
        # Ensure social_media directory exists
        POST_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(POST_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        logger.info(f"Post history saved to {POST_HISTORY_FILE}")
    except Exception as e:
        logger.error(f"Failed to save post history: {e}")
        raise


def _save_post_to_history(platform: str, post_id: str, content: Dict[str, Any]):
    """Save a new post to the history file"""
    history = _load_post_history()

    post_record = {
        "post_id": post_id,
        "platform": platform,
        "content": content,
        "created_at": datetime.now().isoformat(),
        "status": "published"
    }

    history["posts"].append(post_record)
    _save_post_history(history)


@with_graceful_degradation(
    service_name="Facebook Posting API",
    fallbacks=[FallbackMethod.SKIP_WITH_LOG]
)
def post_to_facebook(message: str) -> Dict[str, Any]:
    """
    Post a message to Facebook (Mock API)

    Args:
        message: The message text to post

    Returns:
        Dictionary containing post_id, platform, status, and timestamp

    Raises:
        ValueError: If message is empty or too long (>63,206 characters)
    """
    # Validate input
    if not message or not message.strip():
        raise ValueError("Message cannot be empty")

    if len(message) > 63206:  # Facebook character limit
        raise ValueError(f"Message exceeds Facebook's 63,206 character limit (got {len(message)})")

    # Generate post ID
    post_id = _generate_post_id("facebook")

    # Prepare content
    content = {
        "message": message.strip(),
        "type": "text"
    }

    # Save to post history
    _save_post_to_history("facebook", post_id, content)

    # Log to audit
    audit_logger.log_post_created("facebook", post_id, content)

    logger.info(f"Facebook post created: {post_id}")

    return {
        "post_id": post_id,
        "platform": "facebook",
        "status": "published",
        "timestamp": datetime.now().isoformat(),
        "content": content
    }


@with_graceful_degradation(
    service_name="Instagram Posting API",
    fallbacks=[FallbackMethod.SKIP_WITH_LOG]
)
def post_to_instagram(image_path: str, caption: str) -> Dict[str, Any]:
    """
    Post an image with caption to Instagram (Mock API)

    Args:
        image_path: Path to the image file
        caption: Caption text for the post

    Returns:
        Dictionary containing post_id, platform, status, and timestamp

    Raises:
        ValueError: If image_path is invalid or caption is too long (>2,200 characters)
        FileNotFoundError: If image file doesn't exist
    """
    # Validate input
    if not image_path or not image_path.strip():
        raise ValueError("Image path cannot be empty")

    if not caption or not caption.strip():
        raise ValueError("Caption cannot be empty")

    if len(caption) > 2200:  # Instagram caption limit
        raise ValueError(f"Caption exceeds Instagram's 2,200 character limit (got {len(caption)})")

    # Check if image exists (for mock, we'll log but not require actual file)
    image_exists = os.path.exists(image_path)
    if not image_exists:
        logger.warning(f"Image file not found: {image_path} (continuing with mock)")

    # Generate post ID
    post_id = _generate_post_id("instagram")

    # Prepare content
    content = {
        "image_path": image_path.strip(),
        "image_exists": image_exists,
        "caption": caption.strip(),
        "type": "image"
    }

    # Save to post history
    _save_post_to_history("instagram", post_id, content)

    # Log to audit
    audit_logger.log_post_created("instagram", post_id, content)

    logger.info(f"Instagram post created: {post_id}")

    return {
        "post_id": post_id,
        "platform": "instagram",
        "status": "published",
        "timestamp": datetime.now().isoformat(),
        "content": content
    }


@with_graceful_degradation(
    service_name="Twitter Posting API",
    fallbacks=[FallbackMethod.SKIP_WITH_LOG]
)
def post_to_twitter(tweet_text: str) -> Dict[str, Any]:
    """
    Post a tweet to Twitter (Mock API)

    Args:
        tweet_text: The tweet text (max 280 characters for standard Twitter)

    Returns:
        Dictionary containing post_id, platform, status, and timestamp

    Raises:
        ValueError: If tweet_text is empty or too long (>280 characters)
    """
    # Validate input
    if not tweet_text or not tweet_text.strip():
        raise ValueError("Tweet text cannot be empty")

    if len(tweet_text) > 280:  # Twitter character limit
        raise ValueError(f"Tweet exceeds Twitter's 280 character limit (got {len(tweet_text)})")

    # Generate post ID
    post_id = _generate_post_id("twitter")

    # Prepare content
    content = {
        "tweet_text": tweet_text.strip(),
        "type": "tweet"
    }

    # Save to post history
    _save_post_to_history("twitter", post_id, content)

    # Log to audit
    audit_logger.log_post_created("twitter", post_id, content)

    logger.info(f"Twitter post created: {post_id}")

    return {
        "post_id": post_id,
        "platform": "twitter",
        "status": "published",
        "timestamp": datetime.now().isoformat(),
        "content": content
    }


@with_graceful_degradation(
    service_name="Social Media Summary API",
    fallbacks=[FallbackMethod.SKIP_WITH_LOG]
)
def get_social_summary(hours: int = 24) -> Dict[str, Any]:
    """
    Get a summary of posts from the last N hours

    Args:
        hours: Number of hours to look back (default: 24)

    Returns:
        Dictionary containing summary statistics and recent posts
    """
    # Load post history
    history = _load_post_history()

    # Calculate cutoff time
    cutoff_time = datetime.now() - timedelta(hours=hours)
    cutoff_iso = cutoff_time.isoformat()

    # Filter posts within the time range
    recent_posts = []
    platform_counts = {
        "facebook": 0,
        "instagram": 0,
        "twitter": 0
    }

    for post in history.get("posts", []):
        post_time = datetime.fromisoformat(post.get("created_at", ""))
        if post_time >= cutoff_time:
            recent_posts.append({
                "post_id": post.get("post_id"),
                "platform": post.get("platform"),
                "created_at": post.get("created_at"),
                "status": post.get("status"),
                "content_summary": _get_content_summary(post.get("content", {}), post.get("platform"))
            })
            platform = post.get("platform", "unknown")
            if platform in platform_counts:
                platform_counts[platform] += 1

    # Sort by creation time (newest first)
    recent_posts.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    # Build summary
    summary = {
        "summary_period": {
            "hours": hours,
            "cutoff_time": cutoff_iso,
            "generated_at": datetime.now().isoformat()
        },
        "statistics": {
            "total_posts": len(recent_posts),
            "by_platform": platform_counts,
            "facebook_posts": platform_counts["facebook"],
            "instagram_posts": platform_counts["instagram"],
            "twitter_posts": platform_counts["twitter"]
        },
        "recent_posts": recent_posts[:10],  # Return last 10 posts max
        "all_posts_in_period": recent_posts
    }

    # Log to audit
    audit_logger.log_summary_generated(
        posts_count=len(recent_posts),
        platforms=[p for p, count in platform_counts.items() if count > 0]
    )

    logger.info(f"Social summary generated: {len(recent_posts)} posts in last {hours}h")

    return summary


def _get_content_summary(content: Dict[str, Any], platform: str) -> str:
    """Get a brief summary of post content for display"""
    if platform == "facebook":
        message = content.get("message", "")
        return message[:100] + "..." if len(message) > 100 else message
    elif platform == "instagram":
        caption = content.get("caption", "")
        image_path = content.get("image_path", "")
        return f"[Image: {os.path.basename(image_path)}] {caption[:50]}..." if len(caption) > 50 else f"[Image: {os.path.basename(image_path)}] {caption}"
    elif platform == "twitter":
        tweet_text = content.get("tweet_text", "")
        return tweet_text[:100] + "..." if len(tweet_text) > 100 else tweet_text
    return str(content)


# Export all public functions
__all__ = [
    "post_to_facebook",
    "post_to_instagram",
    "post_to_twitter",
    "get_social_summary",
    "SocialMediaAuditLogger",
    "POST_HISTORY_FILE"
]


if __name__ == "__main__":
    # Demo/test the social media manager
    print("=" * 70)
    print("SOCIAL MEDIA MANAGER - Demo")
    print("=" * 70)

    # Post to Facebook
    print("\n1. Posting to Facebook...")
    fb_result = post_to_facebook("Hello from our AI Employee! 🚀 #GoldTier #Automation")
    print(f"   ✓ Facebook Post ID: {fb_result['post_id']}")

    # Post to Instagram
    print("\n2. Posting to Instagram...")
    ig_result = post_to_instagram(
        "images/sample_post.jpg",
        "Beautiful day at the office! 💼 #WorkLife #GoldTier"
    )
    print(f"   ✓ Instagram Post ID: {ig_result['post_id']}")

    # Post to Twitter
    print("\n3. Posting to Twitter...")
    tw_result = post_to_twitter("Just automated our social media with our AI Employee! 🤖 #AI #Automation")
    print(f"   ✓ Twitter Post ID: {tw_result['post_id']}")

    # Get summary
    print("\n4. Getting 24h summary...")
    summary = get_social_summary()
    print(f"   ✓ Total posts in last 24h: {summary['statistics']['total_posts']}")
    print(f"   • Facebook: {summary['statistics']['facebook_posts']}")
    print(f"   • Instagram: {summary['statistics']['instagram_posts']}")
    print(f"   • Twitter: {summary['statistics']['twitter_posts']}")

    print("\n" + "=" * 70)
    print("Demo completed successfully!")
    print("=" * 70)
