"""
LinkedIn Safety Guardrails
===========================
Implements safety limits and human-like behavior for LinkedIn automation.

Features:
- Daily post limit (max 2 posts per 24 hours)
- Post tracking with JSON file (post_tracker.json)
- Random delays (60-120 seconds) before posting to mimic human behavior
- Automatic skip when daily limit is reached

Usage:
    from linkedin_safety import check_daily_limit, apply_human_delay
    
    # Check if we can post today
    if not check_daily_limit()['can_post']:
        logger.info("Daily limit reached. Post skipped for safety.")
        return
    
    # Apply human-like delay before posting
    apply_human_delay()
    
    # Then proceed with posting
    post_to_linkedin(...)
"""

import os
import sys
import json
import random
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LinkedInSafety")

# Constants
POST_TRACKER_FILE = Path("post_tracker.json")
MAX_DAILY_POSTS = 2  # Maximum posts per 24 hours
MIN_DELAY_SECONDS = 60  # Minimum random delay
MAX_DELAY_SECONDS = 120  # Maximum random delay


def load_post_tracker() -> Dict[str, Any]:
    """
    Load post tracker data from JSON file
    
    Returns:
        Dictionary containing tracking data or default structure
    """
    default_tracker = {
        "last_post_timestamp": None,
        "daily_count": 0,
        "last_reset_date": None,
        "total_posts": 0
    }
    
    if POST_TRACKER_FILE.exists():
        try:
            with open(POST_TRACKER_FILE, 'r', encoding='utf-8') as f:
                tracker = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**default_tracker, **tracker}
        except Exception as e:
            logger.error(f"Failed to load post tracker: {e}")
            return default_tracker
    
    return default_tracker


def save_post_tracker(tracker: Dict[str, Any]):
    """
    Save post tracker data to JSON file
    
    Args:
        tracker: Dictionary containing tracking data
    """
    try:
        with open(POST_TRACKER_FILE, 'w', encoding='utf-8') as f:
            json.dump(tracker, f, indent=2)
        logger.debug("Post tracker saved successfully")
    except Exception as e:
        logger.error(f"Failed to save post tracker: {e}")


def reset_daily_count_if_needed(tracker: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reset daily count if a new day has started (24-hour window from first post)
    
    Args:
        tracker: Current tracker data
        
    Returns:
        Updated tracker data
    """
    today = datetime.now().date().isoformat()
    
    # If no posts yet or it's a new day, reset the count
    if tracker["last_reset_date"] != today:
        # Check if 24 hours have passed since last post
        if tracker["last_post_timestamp"]:
            last_post = datetime.fromisoformat(tracker["last_post_timestamp"])
            hours_since_last = (datetime.now() - last_post).total_seconds() / 3600
            
            # Reset if more than 24 hours since last post OR it's a new calendar day
            if hours_since_last >= 24 or tracker["last_reset_date"] != today:
                logger.info(f"Resetting daily post count (new day: {today})")
                tracker["daily_count"] = 0
                tracker["last_reset_date"] = today
                save_post_tracker(tracker)
        else:
            # First time initialization
            tracker["last_reset_date"] = today
            tracker["daily_count"] = 0
            save_post_tracker(tracker)
    
    return tracker


def check_daily_limit() -> Dict[str, Any]:
    """
    Check if daily LinkedIn post limit has been reached
    
    Returns:
        Dictionary containing:
        - can_post: bool - Whether a post can be made today
        - daily_count: int - Current daily post count
        - max_posts: int - Maximum allowed posts per day
        - last_post_timestamp: str - ISO timestamp of last post
        - message: str - Status message
    """
    tracker = load_post_tracker()
    tracker = reset_daily_count_if_needed(tracker)
    
    can_post = tracker["daily_count"] < MAX_DAILY_POSTS
    
    result = {
        "can_post": can_post,
        "daily_count": tracker["daily_count"],
        "max_posts": MAX_DAILY_POSTS,
        "last_post_timestamp": tracker["last_post_timestamp"],
        "remaining_posts": MAX_DAILY_POSTS - tracker["daily_count"] if can_post else 0,
        "message": ""
    }
    
    if can_post:
        result["message"] = f"Daily limit OK: {tracker['daily_count']}/{MAX_DAILY_POSTS} posts today"
        logger.info(f"✓ LinkedIn Safety Check: {result['message']}")
    else:
        result["message"] = "Daily LinkedIn limit reached. Post skipped for safety."
        logger.warning(f"⚠️  LinkedIn Safety Check: {result['message']}")
    
    return result


def record_post():
    """
    Record a successful post in the tracker
    Updates the daily count and timestamp
    """
    tracker = load_post_tracker()
    tracker = reset_daily_count_if_needed(tracker)
    
    tracker["daily_count"] += 1
    tracker["last_post_timestamp"] = datetime.now().isoformat()
    tracker["total_posts"] = tracker.get("total_posts", 0) + 1
    
    save_post_tracker(tracker)
    
    logger.info(f"Post recorded: {tracker['daily_count']}/{MAX_DAILY_POSTS} posts today")


def apply_human_delay():
    """
    Apply a random delay (60-120 seconds) to mimic human behavior before posting
    
    This delay helps avoid detection as automated behavior by:
    - Adding unpredictable wait time
    - Simulating human hesitation before clicking post
    - Reducing the risk of platform rate limiting
    """
    delay_seconds = random.randint(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
    
    logger.info(f"🕐 Applying human-like delay: {delay_seconds} seconds before posting...")
    logger.info(f"   (This mimics natural human hesitation before clicking 'Post')")
    
    # Log progress at intervals
    intervals = min(3, delay_seconds // 20)  # Log 2-3 times during delay
    interval_duration = delay_seconds // (intervals + 1)
    
    for i in range(intervals):
        time.sleep(interval_duration)
        elapsed = (i + 1) * interval_duration
        remaining = delay_seconds - elapsed
        logger.debug(f"   ... {remaining} seconds remaining")
    
    # Final sleep to complete the exact delay
    time.sleep(max(0, delay_seconds - intervals * interval_duration))
    
    logger.info(f"✓ Delay complete. Proceeding with post.")


def get_tracker_status() -> Dict[str, Any]:
    """
    Get current tracker status for display/debugging
    
    Returns:
        Dictionary with current tracking status
    """
    tracker = load_post_tracker()
    tracker = reset_daily_count_if_needed(tracker)
    
    return {
        "daily_count": tracker["daily_count"],
        "max_posts": MAX_DAILY_POSTS,
        "remaining_posts": max(0, MAX_DAILY_POSTS - tracker["daily_count"]),
        "last_post": tracker["last_post_timestamp"],
        "total_posts_all_time": tracker.get("total_posts", 0),
        "tracker_file": str(POST_TRACKER_FILE.absolute())
    }


def reset_tracker():
    """
    Reset the post tracker (for testing or manual override)
    """
    tracker = {
        "last_post_timestamp": None,
        "daily_count": 0,
        "last_reset_date": datetime.now().date().isoformat(),
        "total_posts": 0
    }
    save_post_tracker(tracker)
    logger.info("Post tracker has been reset")


def main():
    """Main function for testing safety guardrails"""
    print("=" * 70)
    print("LINKEDIN SAFETY GUARDRAILS - Test & Status")
    print("=" * 70)
    print()
    
    # Check daily limit
    print("1. Checking Daily Post Limit...")
    print("-" * 70)
    limit_check = check_daily_limit()
    print(f"   Can Post Today: {limit_check['can_post']}")
    print(f"   Posts Today: {limit_check['daily_count']}/{limit_check['max_posts']}")
    if limit_check['can_post']:
        print(f"   Remaining: {limit_check['remaining_posts']} post(s)")
    print(f"   Last Post: {limit_check['last_post_timestamp'] or 'None'}")
    print(f"   Status: {limit_check['message']}")
    print()
    
    # Show tracker status
    print("2. Tracker File Status...")
    print("-" * 70)
    status = get_tracker_status()
    print(f"   Tracker File: {status['tracker_file']}")
    print(f"   Daily Count: {status['daily_count']}/{status['max_posts']}")
    print(f"   Remaining Today: {status['remaining_posts']}")
    print(f"   Last Post: {status['last_post'] or 'None'}")
    print(f"   Total Posts (All Time): {status['total_posts_all_time']}")
    print()
    
    # Test human delay (optional)
    print("3. Human Delay Test...")
    print("-" * 70)
    response = input(f"   Test {MIN_DELAY_SECONDS}-{MAX_DELAY_SECONDS}s delay? (y/n): ").strip().lower()
    
    if response == 'y':
        print()
        apply_human_delay()
        print()
        print("   ✓ Delay test complete!")
    else:
        print("   Skipped delay test")
    
    print()
    print("=" * 70)
    print("Safety guardrails test complete!")
    print("=" * 70)
    
    return limit_check


if __name__ == "__main__":
    main()
