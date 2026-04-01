#!/usr/bin/env python3
"""
LinkedIn Authentication Helper
===============================
This script helps you authenticate to LinkedIn and save session cookies.
Run this ONCE to set up authentication, then the main automation will work automatically.

Usage:
    python linkedin_auth.py
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Enable UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

# Constants
LINKEDIN_COOKIE_FILE = Path("linkedin_cookies.json")
LINKEDIN_URL = "https://www.linkedin.com"


async def authenticate_linkedin():
    """
    Authenticate with LinkedIn and save session cookies

    Returns:
        True if authentication successful, False otherwise
    """
    from playwright.async_api import async_playwright

    print("=" * 70)
    print("LINKEDIN AUTHENTICATION HELPER")
    print("=" * 70)
    print()
    print("📋 INSTRUCTIONS:")
    print("1. A browser window will open")
    print("2. Log in to your LinkedIn account")
    print("3. Wait for the LinkedIn feed to load")
    print("4. The script will automatically save your session")
    print("5. Close the browser when you see 'Authentication complete!'")
    print()

    input("Press Enter to open the browser...")

    try:
        async with async_playwright() as p:
            # Launch browser in HEADLESS=FALSE mode so you can see and interact
            browser = await p.chromium.launch(
                headless=False,  # IMPORTANT: Must be False for manual login
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--start-maximized'
                ]
            )

            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            page = await context.new_page()

            print("\n🌐 Opening LinkedIn...")
            await page.goto(LINKEDIN_URL, wait_until='networkidle', timeout=60000)

            print("\n⏳ Waiting for you to log in...")
            print("   (The script will detect when you're logged in)")
            print()

            # Wait for login - check every 5 seconds for up to 5 minutes
            max_attempts = 60  # 5 minutes / 5 seconds
            attempt = 0

            while attempt < max_attempts:
                await asyncio.sleep(5)
                attempt += 1

                # Check if logged in by looking for feed page or profile elements
                current_url = page.url

                # Check for login success indicators
                is_logged_in = False

                if 'feed' in current_url or 'mynetwork' in current_url or 'jobs' in current_url:
                    # We're on a post-login page
                    is_logged_in = True

                # Also check for profile icon or other logged-in elements
                try:
                    profile_selector = '.nav-item__link--profile'
                    profile_element = await page.query_selector(profile_selector)
                    if profile_element:
                        is_logged_in = True
                except:
                    pass

                if is_logged_in:
                    print("\n✅ Login detected!")
                    print("   Waiting a moment for session to stabilize...")
                    await asyncio.sleep(3)

                    # Get cookies
                    cookies = await context.cookies()

                    # Filter only LinkedIn cookies
                    linkedin_cookies = [c for c in cookies if 'linkedin.com' in c.get('domain', '')]

                    if linkedin_cookies:
                        # Save cookies
                        with open(LINKEDIN_COOKIE_FILE, 'w', encoding='utf-8') as f:
                            json.dump(linkedin_cookies, f, indent=2)

                        print(f"\n💾 Saved {len(linkedin_cookies)} cookies to {LINKEDIN_COOKIE_FILE}")
                        print("\n🎉 Authentication complete!")
                        print("\n✅ You can now close this window.")
                        print("   Your AI Employee will use these cookies for future LinkedIn posts.")

                        await asyncio.sleep(5)
                        await browser.close()
                        return True
                    else:
                        print("\n⚠️  No LinkedIn cookies found. Please try again.")

                else:
                    # Still waiting for login
                    if attempt % 15 == 0:  # Every 75 seconds
                        print(f"   Still waiting... ({attempt * 5}s elapsed)")
                        print(f"   Current page: {current_url}")

            # Timeout
            print("\n⏰ Timeout reached (5 minutes)")
            print("   Please try again if you're still logging in.")
            await browser.close()
            return False

    except Exception as e:
        print(f"\n❌ Error during authentication: {e}")
        print("\nPlease check your internet connection and try again.")
        return False


def verify_authentication():
    """
    Verify that LinkedIn authentication is set up correctly

    Returns:
        True if cookies exist and are valid, False otherwise
    """
    if not LINKEDIN_COOKIE_FILE.exists():
        print("❌ No LinkedIn cookies found.")
        print("   Run 'python linkedin_auth.py' to authenticate.")
        return False

    try:
        with open(LINKEDIN_COOKIE_FILE, 'r', encoding='utf-8') as f:
            cookies = json.load(f)

        if not cookies or len(cookies) == 0:
            print("❌ Cookie file is empty.")
            print("   Run 'python linkedin_auth.py' to authenticate.")
            return False

        # Check for essential LinkedIn cookies
        essential_cookies = ['li_at', 'JSESSIONID']
        cookie_names = [c.get('name', '') for c in cookies]

        has_auth = any(name in cookie_names for name in essential_cookies)

        if has_auth:
            print(f"✅ Authentication verified! ({len(cookies)} cookies)")
            return True
        else:
            print("⚠️  Cookies may be invalid (missing authentication cookies).")
            print("   Run 'python linkedin_auth.py' to re-authenticate.")
            return False

    except Exception as e:
        print(f"❌ Error reading cookies: {e}")
        return False


def main():
    """Main function"""
    print()

    # Check if already authenticated
    if verify_authentication():
        print("\n" + "=" * 70)
        print("✅ LinkedIn is already authenticated!")
        print("=" * 70)
        print("\nYour AI Employee can post to LinkedIn automatically.")
        print("\nTo re-authenticate (e.g., if posts are failing), run:")
        print("  python linkedin_auth.py")
        print("\nOr delete linkedin_cookies.json and run the script again.")
        print("=" * 70)
        return

    print()
    response = input("Do you want to authenticate with LinkedIn now? (y/n): ").strip().lower()

    if response == 'y':
        print()
        success = asyncio.run(authenticate_linkedin())

        if success:
            print("\n" + "=" * 70)
            print("✅ Setup complete!")
            print("=" * 70)
            print("\nNext time you run the AI Employee:")
            print("  python autonomous_agent.py")
            print("\nIt will automatically post to LinkedIn after processing emails!")
            print("=" * 70)
        else:
            print("\n⚠️  Authentication was not completed.")
            print("   You can try again later by running: python linkedin_auth.py")
    else:
        print("\nℹ️  Skipping authentication.")
        print("   Run 'python linkedin_auth.py' anytime to set up LinkedIn posting.")


if __name__ == "__main__":
    main()
