"""
LinkedIn Automation - Real-Time Direct Poster
==============================================
This script posts directly to LinkedIn using Playwright browser automation.
It integrates with the autonomous agent to post real-time updates about
email processing and Odoo updates.

Features:
- Direct posting to LinkedIn (no drafts)
- Uses Playwright for headless browser automation
- Supports LinkedIn session cookies for authentication
- Posts real-time work summaries with customizable format

Usage:
    python linkedin_automation.py
    or
    from linkedin_automation import post_to_linkedin
    post_to_linkedin("Your message here")
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Enable UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LinkedInAutomation")

# Constants
LINKEDIN_COOKIE_FILE = Path("linkedin_cookies.json")
LINKEDIN_URL = "https://www.linkedin.com"
LINKEDIN_POST_URL = "https://www.linkedin.com/feed/"

# Import safety guardrails
from linkedin_safety import check_daily_limit, apply_human_delay, record_post, MIN_DELAY_SECONDS, MAX_DELAY_SECONDS


def load_linkedin_cookies() -> Optional[list]:
    """
    Load LinkedIn session cookies from JSON file

    Returns:
        List of cookies if file exists, None otherwise
    """
    if LINKEDIN_COOKIE_FILE.exists():
        try:
            with open(LINKEDIN_COOKIE_FILE, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            logger.info("LinkedIn cookies loaded successfully")
            return cookies
        except Exception as e:
            logger.error(f"Failed to load LinkedIn cookies: {e}")
    return None


def save_linkedin_cookies(cookies: list):
    """
    Save LinkedIn session cookies to JSON file

    Args:
        cookies: List of cookie dictionaries
    """
    try:
        with open(LINKEDIN_COOKIE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2)
        logger.info("LinkedIn cookies saved successfully")
    except Exception as e:
        logger.error(f"Failed to save LinkedIn cookies: {e}")


async def post_to_linkedin_direct(message: str, email_count: int, odoo_updates: int = 0) -> Dict[str, Any]:
    """
    Post a message directly to LinkedIn using Playwright

    Args:
        message: The post message content
        email_count: Number of emails processed (for summary format)
        odoo_updates: Number of Odoo updates made

    Returns:
        Dictionary containing post_id, status, timestamp, and message

    Raises:
        Exception: If posting fails
    """
    from playwright.async_api import async_playwright

    timestamp = datetime.now().isoformat()
    post_id = f"linkedin_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    try:
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                headless=True,  # Set to False for debugging
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu'
                ]
            )

            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            page = await context.new_page()

            # Load cookies if available
            cookies = load_linkedin_cookies()
            if cookies:
                await context.add_cookies(cookies)
                logger.info("Loaded existing LinkedIn session")

            # Navigate to LinkedIn
            logger.info("Navigating to LinkedIn...")
            await page.goto(LINKEDIN_URL, wait_until='networkidle', timeout=60000)

            # Check if logged in by looking for specific elements
            await page.wait_for_timeout(5000)  # Wait for page to load

            # Check if we're on login page (not authenticated)
            current_url = page.url
            if 'login' in current_url or 'checkpoint' in current_url:
                logger.error("Not logged in to LinkedIn. Please authenticate first.")
                await browser.close()
                raise Exception(
                    "LinkedIn authentication required. "
                    "Please log in manually at linkedin.com and run the authentication flow."
                )

            # Navigate to post creation page
            logger.info("Navigating to post creation...")
            await page.goto(LINKEDIN_POST_URL, wait_until='networkidle', timeout=60000)
            await page.wait_for_timeout(3000)

            # Find and click the post creation box
            logger.info("Opening post composer...")
            
            # Try multiple selectors for the post input
            post_selectors = [
                'div[role="textbox"][aria-label*="post"]',
                'div[aria-label*="Start a post"]',
                'button:has-text("Start a post")',
                '.share-box-feed-entry__trigger',
                '[data-id="urn:li:org-guest-feed-compose-trigger"]'
            ]
            
            post_input = None
            for selector in post_selectors:
                try:
                    post_input = await page.wait_for_selector(selector, timeout=5000)
                    if post_input:
                        logger.info(f"Found post trigger with selector: {selector}")
                        break
                except:
                    continue

            if post_input:
                await post_input.click()
                await page.wait_for_timeout(2000)
            else:
                logger.warning("Could not find post trigger, trying alternative approach")

            # Find the text editor and type the message
            logger.info("Entering post content...")
            
            # LinkedIn uses a contenteditable div for the post editor
            editor_selectors = [
                'div[contenteditable="true"][role="textbox"]',
                'div[aria-label*="What do you want to share?"]',
                '.editor-content-area[contenteditable="true"]',
                'div.ql-editor[contenteditable="true"]'
            ]
            
            editor = None
            for selector in editor_selectors:
                try:
                    editor = await page.wait_for_selector(selector, timeout=3000)
                    if editor:
                        logger.info(f"Found editor with selector: {selector}")
                        break
                except:
                    continue

            if editor:
                # Clear any existing content and type new message
                await editor.fill('')
                await editor.type(message, delay=50)  # Type with delay to simulate human
                await page.wait_for_timeout(1000)

                # Find and click the post button
                logger.info("Submitting post...")
                
                post_button_selectors = [
                    'button:has-text("Post")',
                    'button[aria-label*="Post"]',
                    '.share-actions__primary-action button'
                ]
                
                post_button = None
                for selector in post_button_selectors:
                    try:
                        post_button = await page.wait_for_selector(selector, timeout=3000)
                        if post_button and await post_button.is_enabled():
                            logger.info(f"Found post button with selector: {selector}")
                            break
                    except:
                        continue

                if post_button:
                    # SAFETY GUARDRAIL: Apply human-like delay before clicking post button
                    logger.info("Safety Guardrail: Applying human-like delay before posting...")
                    await page.wait_for_timeout(5000)  # 5 second delay in browser (full 60-120s done in wrapper)
                    
                    await post_button.click()
                    await page.wait_for_timeout(3000)

                    logger.info("Post submitted successfully!")

                    # Save cookies for future use
                    cookies = await context.cookies()
                    save_linkedin_cookies(cookies)
                    
                    # Record the post in tracker
                    record_post()

                    return {
                        'post_id': post_id,
                        'platform': 'linkedin',
                        'status': 'published',
                        'timestamp': timestamp,
                        'message': message,
                        'email_count': email_count,
                        'odoo_updates': odoo_updates
                    }
                else:
                    raise Exception("Could not find Post button")
            else:
                raise Exception("Could not find post editor")

            await browser.close()

    except Exception as e:
        logger.error(f"LinkedIn posting failed: {e}")
        raise


def post_to_linkedin_fallback(message: str, email_count: int, odoo_updates: int = 0) -> Dict[str, Any]:
    """
    Fallback method: Save post to file if Playwright fails
    This ensures we always have a record even if direct posting fails

    Args:
        message: The post message content
        email_count: Number of emails processed
        odoo_updates: Number of Odoo updates made

    Returns:
        Dictionary containing post info
    """
    logger.warning("Using fallback method - saving post to file")
    
    timestamp = datetime.now().isoformat()
    post_id = f"linkedin_draft_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Create drafts directory
    drafts_dir = Path("linkedin_drafts")
    drafts_dir.mkdir(exist_ok=True)
    
    # Save post to file
    filename = f"linkedin_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = drafts_dir / filename
    
    post_content = f"""
================================================================================
LINKEDIN POST - READY TO PUBLISH
Generated: {timestamp}
================================================================================

{message}

================================================================================
METADATA
================================================================================
Emails Processed: {email_count}
Odoo Updates: {odoo_updates}
Post ID: {post_id}
Status: Ready for manual posting (fallback mode)
================================================================================

INSTRUCTIONS:
1. Copy the message above
2. Go to linkedin.com/feed
3. Click "Start a post"
4. Paste the message
5. Click "Post"
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(post_content)
    
    logger.info(f"Post saved to {filepath}")
    
    return {
        'post_id': post_id,
        'platform': 'linkedin',
        'status': 'saved_for_manual_posting',
        'timestamp': timestamp,
        'message': message,
        'email_count': email_count,
        'odoo_updates': odoo_updates,
        'filepath': str(filepath)
    }


def post_to_linkedin(message: str, email_count: int, odoo_updates: int = 0, use_fallback: bool = False) -> Dict[str, Any]:
    """
    Main function to post to LinkedIn
    Tries direct posting first, falls back to file saving if needed
    
    Safety Guardrails:
    - Checks daily post limit (max 2 posts per 24 hours)
    - Applies random 60-120 second delay before posting to mimic human behavior

    Args:
        message: The post message content
        email_count: Number of emails processed
        odoo_updates: Number of Odoo updates made
        use_fallback: If True, skip direct posting and use fallback

    Returns:
        Dictionary containing post results
    """
    logger.info("=" * 70)
    logger.info("LINKEDIN REAL-TIME POSTING")
    logger.info("=" * 70)
    logger.info(f"Emails processed: {email_count}")
    logger.info(f"Odoo updates: {odoo_updates}")
    logger.info(f"Message: {message[:100]}...")

    # SAFETY GUARDRAIL 1: Check daily post limit
    logger.info("Safety Check: Verifying daily post limit...")
    limit_status = check_daily_limit()
    
    if not limit_status['can_post']:
        logger.warning(f"Daily LinkedIn limit reached. Post skipped for safety.")
        print(f"   ⚠️  {limit_status['message']}")
        return {
            'post_id': None,
            'platform': 'linkedin',
            'status': 'skipped_safety_limit',
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'email_count': email_count,
            'odoo_updates': odoo_updates,
            'reason': 'daily_limit_reached',
            'daily_count': limit_status['daily_count'],
            'max_posts': limit_status['max_posts']
        }
    
    logger.info(f"✓ Safety Check Passed: {limit_status['message']}")

    if use_fallback:
        return post_to_linkedin_fallback(message, email_count, odoo_updates)

    try:
        import asyncio

        # Check if playwright is installed
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.error("Playwright not installed. Install with: playwright install")
            return post_to_linkedin_fallback(message, email_count, odoo_updates)

        # SAFETY GUARDRAIL 2: Apply human-like delay before posting
        logger.info(f"Applying human-like delay ({MIN_DELAY_SECONDS}-{MAX_DELAY_SECONDS} seconds)...")
        print(f"   🕐 Waiting {MIN_DELAY_SECONDS}-{MAX_DELAY_SECONDS} seconds (human behavior simulation)...")
        apply_human_delay()

        # Run async function
        result = asyncio.run(post_to_linkedin_direct(message, email_count, odoo_updates))

        logger.info("✓ LinkedIn post published successfully!")
        logger.info(f"Post ID: {result['post_id']}")
        logger.info("=" * 70)

        return result

    except Exception as e:
        logger.error(f"Direct posting failed: {e}")
        logger.info("Falling back to save-to-file method...")
        return post_to_linkedin_fallback(message, email_count, odoo_updates)


def generate_linkedin_summary(email_count: int, odoo_updates: int = 0) -> str:
    """
    Generate the standard LinkedIn summary message

    Args:
        email_count: Number of emails processed
        odoo_updates: Number of Odoo updates made

    Returns:
        Formatted LinkedIn post message
    """
    # Use the exact format specified in the requirements
    summary = f"Today my AI Employee (on Lenovo X260) processed {email_count} emails and updated Odoo! #GIAIC #AI_Employee"
    
    if odoo_updates > 0:
        summary += f" ({odoo_updates} new customers added)"
    
    summary += " 🚀🤖"
    
    return summary


def main():
    """Main function for testing LinkedIn posting"""
    print("=" * 70)
    print("LINKEDIN AUTOMATION - REAL-TIME POSTER")
    print("=" * 70)
    print()

    # Test with sample data
    test_email_count = 5
    test_odoo_updates = 2
    
    # Generate summary message
    message = generate_linkedin_summary(test_email_count, test_odoo_updates)
    
    print(f"📝 Post Message:\n{message}\n")
    print("-" * 70)
    
    # Ask user if they want to test posting
    print("\n⚠️  NOTE: To use real-time posting, you need to:")
    print("1. Have Playwright installed: pip install playwright")
    print("2. Install browser: playwright install chromium")
    print("3. Be logged in to LinkedIn (cookies will be saved)")
    print()
    
    response = input("Do you want to test posting to LinkedIn? (y/n): ").strip().lower()
    
    if response == 'y':
        print("\n🚀 Attempting to post to LinkedIn...")
        try:
            result = post_to_linkedin(message, test_email_count, test_odoo_updates)
            
            if result['status'] == 'published':
                print("\n✅ SUCCESS! Post published to LinkedIn!")
                print(f"   Post ID: {result['post_id']}")
            else:
                print("\n⚠️  Post saved for manual posting")
                print(f"   File: {result.get('filepath', 'N/A')}")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nFalling back to draft mode...")
            result = post_to_linkedin_fallback(message, test_email_count, test_odoo_updates)
            print(f"Draft saved to: {result['filepath']}")
    else:
        print("\n💾 Saving as draft for review...")
        result = post_to_linkedin_fallback(message, test_email_count, test_odoo_updates)
        print(f"Draft saved to: {result['filepath']}")
    
    print("\n" + "=" * 70)
    print("Test completed!")
    print("=" * 70)
    
    return result


if __name__ == "__main__":
    main()
