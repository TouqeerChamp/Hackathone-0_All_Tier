#!/usr/bin/env python3
"""
Autonomous Agent - Ralph Wiggum Loop Implementation
====================================================
Gold Tier autonomous multi-step task processor.

This script implements the Ralph Wiggum Loop for autonomous task execution:
1. Scan inbox for new emails
2. For each complex email, check if sender exists in Odoo
3. If sender is new, create customer record in Odoo
4. Log every step to audit_logs/
5. Provide CEO Summary of actions taken

Usage:
    python autonomous_agent.py
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Enable UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Import local modules
from inbox_scanner import scan_inbox, process_email_file, categorize_task
from odoo_client import get_odoo_connection, execute_odoo_query, ODOO_URL
from social_media.social_manager import (
    post_to_facebook,
    post_to_instagram,
    post_to_twitter,
    get_social_summary
)
from linkedin_automation import post_to_linkedin, generate_linkedin_summary

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AutonomousAgent")

# Constants
AUDIT_LOG_DIR = "logs/audit_logs"
INBOX_DIR = "inbox"
HEARTBEAT_LOG = Path(AUDIT_LOG_DIR) / "heartbeat.log"


class AuditLogger:
    """Gold Tier compliant audit logger for autonomous agent actions"""
    
    def __init__(self, log_dir: str = AUDIT_LOG_DIR):
        self.log_dir = log_dir
        self._ensure_log_directory()
        self.log_file = self._get_daily_log_file()
    
    def _ensure_log_directory(self):
        """Create audit log directory if it doesn't exist"""
        os.makedirs(self.log_dir, exist_ok=True)
    
    def _get_daily_log_file(self) -> str:
        """Get today's audit log file path"""
        today = datetime.now().strftime("%Y%m%d")
        return os.path.join(self.log_dir, f"autonomous_agent_{today}.log")
    
    def log(self, event_type: str, status: str, details: Dict[str, Any]):
        """
        Log an audit event in JSON Lines format
        
        Args:
            event_type: Type of event (e.g., 'email_processed', 'customer_created')
            status: Event status ('success', 'error', 'skipped')
            details: Dictionary containing event details
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "status": status,
            "agent": "Ralph_Wiggum_Loop",
            "details": details
        }
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            logger.info(f"Audit: {event_type} - {status}")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def log_email_processed(self, email_file: str, category: str, sender: str):
        """Log email processing event"""
        self.log(
            event_type="email_processed",
            status="success",
            details={
                "email_file": email_file,
                "category": category,
                "sender": sender
            }
        )
    
    def log_odoo_check(self, sender_email: str, exists: bool, customer_data: Optional[Dict] = None):
        """Log Odoo customer check event"""
        self.log(
            event_type="odoo_customer_check",
            status="success",
            details={
                "sender_email": sender_email,
                "exists_in_odoo": exists,
                "customer_data": customer_data
            }
        )
    
    def log_customer_created(self, sender_email: str, customer_id: int, customer_name: str):
        """Log new customer creation event"""
        self.log(
            event_type="customer_created",
            status="success",
            details={
                "sender_email": sender_email,
                "odoo_customer_id": customer_id,
                "customer_name": customer_name
            }
        )
    
    def log_customer_creation_failed(self, sender_email: str, error: str):
        """Log failed customer creation event"""
        self.log(
            event_type="customer_creation_failed",
            status="error",
            details={
                "sender_email": sender_email,
                "error": error
            }
        )

    def log_loop_completed(self, emails_processed: int, customers_added: int):
        """Log completion of Ralph Wiggum Loop cycle"""
        self.log(
            event_type="ralph_wiggum_loop_completed",
            status="success",
            details={
                "emails_processed": emails_processed,
                "customers_added": customers_added,
                "cycle_completed_at": datetime.now().isoformat()
            }
        )

    def log_social_media_post(self, platform: str, post_id: str, message: str):
        """Log social media post creation"""
        self.log(
            event_type="social_media_post",
            status="success",
            details={
                "platform": platform,
                "post_id": post_id,
                "message": message
            }
        )

    def log_social_media_post_failed(self, platform: str, error: str, message: str):
        """Log failed social media post creation"""
        self.log(
            event_type="social_media_post_failed",
            status="error",
            details={
                "platform": platform,
                "error": error,
                "message": message
            }
        )

    def log_linkedin_post(self, post_id: str, message: str, email_count: int, odoo_updates: int):
        """Log LinkedIn post creation"""
        self.log(
            event_type="linkedin_post",
            status="success",
            details={
                "post_id": post_id,
                "message": message,
                "email_count": email_count,
                "odoo_updates": odoo_updates
            }
        )

    def log_linkedin_post_failed(self, error: str, message: str):
        """Log failed LinkedIn post creation"""
        self.log(
            event_type="linkedin_post_failed",
            status="error",
            details={
                "error": error,
                "message": message
            }
        )


def check_critical_services(audit: AuditLogger) -> bool:
    """
    Check if critical background services (Heartbeat, Gmail Watcher) are operational.
    Logs CRITICAL message to audit logs if any service is down.
    
    Args:
        audit: AuditLogger instance for logging
        
    Returns:
        True if all services are healthy, False otherwise
    """
    all_healthy = True
    
    # Check Heartbeat service
    if HEARTBEAT_LOG.exists():
        try:
            last_modified = datetime.fromtimestamp(HEARTBEAT_LOG.stat().st_mtime)
            time_since_update = datetime.now() - last_modified
            
            # If heartbeat hasn't been updated in 15 minutes, consider it down
            if time_since_update.total_seconds() > 900:
                logger.error("CRITICAL: Heartbeat service is DOWN (no heartbeat in 15+ minutes)")
                audit.log(
                    event_type="critical_service_failure",
                    status="error",
                    details={
                        "service": "Heartbeat",
                        "message": "CRITICAL: Executive Service Down - Heartbeat monitor not responding",
                        "last_update": last_modified.isoformat(),
                        "seconds_since_update": time_since_update.total_seconds()
                    }
                )
                all_healthy = False
        except Exception as e:
            logger.error(f"CRITICAL: Failed to check Heartbeat service: {e}")
            audit.log(
                event_type="critical_service_failure",
                status="error",
                details={
                    "service": "Heartbeat",
                    "message": f"CRITICAL: Executive Service Down - Error checking heartbeat: {str(e)}"
                }
            )
            all_healthy = False
    else:
        logger.error("CRITICAL: Heartbeat service is DOWN (no heartbeat.log found)")
        audit.log(
            event_type="critical_service_failure",
            status="error",
            details={
                "service": "Heartbeat",
                "message": "CRITICAL: Executive Service Down - Heartbeat log file not found"
            }
        )
        all_healthy = False
    
    # Check Gmail Watcher service (by checking inbox directory)
    if os.path.exists(INBOX_DIR):
        try:
            email_files = [f for f in os.listdir(INBOX_DIR) if f.endswith('.json')]
            if not email_files:
                # No emails processed yet - might be normal on first run
                logger.info("Gmail Watcher: No emails in inbox yet (may be normal)")
            else:
                logger.info(f"Gmail Watcher: {len(email_files)} email(s) in inbox")
        except Exception as e:
            logger.warning(f"Gmail Watcher check warning: {e}")
    else:
        logger.warning("Gmail Watcher: Inbox directory not found")
    
    if all_healthy:
        logger.info("All critical services are operational")
    
    return all_healthy


def get_inbox_emails(inbox_dir: str = INBOX_DIR) -> List[str]:
    """
    Get list of email files in inbox
    
    Returns:
        List of file paths to process
    """
    if not os.path.exists(inbox_dir):
        logger.warning(f"Inbox directory not found: {inbox_dir}")
        return []
    
    json_files = [
        os.path.join(inbox_dir, f) 
        for f in os.listdir(inbox_dir) 
        if f.endswith('.json')
    ]
    
    logger.info(f"Found {len(json_files)} email(s) in inbox")
    return json_files


def parse_email_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Parse an email JSON file and extract key information
    
    Args:
        file_path: Path to the email JSON file
        
    Returns:
        Dictionary with email details or None if parsing fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            email_data = json.loads(f.read())
        
        sender_info = email_data.get('from', {})
        sender_email = sender_info.get('email', 'Unknown')
        sender_name = sender_info.get('name', 'Unknown')
        
        return {
            'file_path': file_path,
            'sender_email': sender_email,
            'sender_name': sender_name,
            'subject': email_data.get('subject', 'No Subject'),
            'body': email_data.get('snippet', ''),
            'date': email_data.get('date', datetime.now().isoformat())
        }
    except Exception as e:
        logger.error(f"Failed to parse email file {file_path}: {e}")
        return None


def check_customer_in_odoo(email: str) -> Tuple[bool, Optional[Dict]]:
    """
    Check if a customer exists in Odoo by email
    
    Args:
        email: Customer email address to search for
        
    Returns:
        Tuple of (exists: bool, customer_data: dict or None)
    """
    try:
        # Search for partner with matching email
        results = execute_odoo_query(
            model='res.partner',
            method='search_read',
            args=[[['email', '=', email]]],
            kwargs={'fields': ['id', 'name', 'email', 'customer_rank'], 'limit': 1}
        )
        
        if results and len(results) > 0:
            customer = results[0]
            logger.info(f"Customer found in Odoo: {customer.get('name')} (ID: {customer.get('id')})")
            return True, customer
        else:
            logger.info(f"No customer found in Odoo for email: {email}")
            return False, None
            
    except Exception as e:
        logger.error(f"Error checking customer in Odoo: {e}")
        return False, None


def create_customer_in_odoo(name: str, email: str) -> Optional[int]:
    """
    Create a new customer record in Odoo

    Args:
        name: Customer name
        email: Customer email address

    Returns:
        New customer ID if successful, None otherwise
    """
    try:
        # Create new partner record with basic fields only
        customer_id = execute_odoo_query(
            model='res.partner',
            method='create',
            args=[{
                'name': name,
                'email': email
            }]
        )

        if customer_id:
            logger.info(f"Created new customer in Odoo: {name} (ID: {customer_id})")
            return customer_id
        else:
            logger.error("Failed to create customer in Odoo - no ID returned")
            return None

    except Exception as e:
        logger.error(f"Error creating customer in Odoo: {e}")
        raise


def ralph_wiggum_loop(audit: AuditLogger) -> Dict[str, int]:
    """
    Execute the Ralph Wiggum Loop for autonomous multi-step task processing

    The Loop:
    1. Scan inbox for new emails
    2. For each email, check if it's complex
    3. For complex emails, check if sender exists in Odoo
    4. If sender is new, create customer record
    5. Log every step

    Args:
        audit: AuditLogger instance for logging

    Returns:
        Dictionary with counts: {'emails_processed': X, 'customers_added': Y}
    """
    print("=" * 70)
    print("RALPH WIGGUM LOOP - Autonomous Multi-Step Task Processor")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)

    stats = {
        'emails_processed': 0,
        'complex_emails': 0,
        'existing_customers': 0,
        'customers_added': 0,
        'errors': 0
    }

    # Step 1: Get emails from inbox
    email_files = get_inbox_emails(INBOX_DIR)

    if not email_files:
        print("No emails to process in inbox.")
        audit.log_loop_completed(0, 0)
        return stats

    print(f"Found {len(email_files)} email(s) to process")
    print("-" * 70)

    # Step 2: Process each email
    for email_file in email_files:
        print(f"\nProcessing: {os.path.basename(email_file)}")

        # Parse email file
        email_data = parse_email_file(email_file)
        if not email_data:
            stats['errors'] += 1
            continue

        sender_email = email_data['sender_email']
        sender_name = email_data['sender_name']
        body = email_data['body']

        # Categorize the email
        category = categorize_task(body)
        stats['emails_processed'] += 1

        audit.log_email_processed(
            email_file=os.path.basename(email_file),
            category=category,
            sender=sender_email
        )

        print(f"  Sender: {sender_name} <{sender_email}>")
        print(f"  Category: {category}")

        # Step 3: Only process complex emails (needs_action)
        if category != 'needs_action':
            print(f"  → Skipping (not complex)")
            continue

        stats['complex_emails'] += 1
        print(f"  → Complex email detected - checking Odoo...")

        # Step 4: Check if sender exists in Odoo
        exists, customer_data = check_customer_in_odoo(sender_email)

        if exists:
            stats['existing_customers'] += 1
            customer_name = customer_data.get('name', 'Unknown') if customer_data else 'Unknown'
            print(f"  → Customer already exists: {customer_name}")
            audit.log_odoo_check(sender_email, exists=True, customer_data=customer_data)
            continue

        # Step 5: Create new customer in Odoo
        print(f"  → New customer detected - creating Odoo record...")

        try:
            # Use sender name if available, otherwise use email
            customer_name = sender_name if sender_name and sender_name != 'Unknown' else sender_email

            customer_id = create_customer_in_odoo(customer_name, sender_email)

            if customer_id:
                stats['customers_added'] += 1
                print(f"  ✓ Customer created successfully (ID: {customer_id})")
                audit.log_customer_created(sender_email, customer_id, customer_name)
            else:
                stats['errors'] += 1
                print(f"  ✗ Failed to create customer")
                audit.log_customer_creation_failed(sender_email, "No customer ID returned")

        except Exception as e:
            stats['errors'] += 1
            error_msg = str(e)
            print(f"  ✗ Error creating customer: {error_msg}")
            audit.log_customer_creation_failed(sender_email, error_msg)

    # Step 6: Log loop completion
    print("\n" + "-" * 70)
    audit.log_loop_completed(
        emails_processed=stats['emails_processed'],
        customers_added=stats['customers_added']
    )

    return stats


def post_work_summary_to_social_media(audit: AuditLogger, stats: Dict[str, int]) -> Dict[str, Any]:
    """
    Post a summary of today's work to all social media platforms including LinkedIn

    Args:
        audit: AuditLogger instance for logging
        stats: Dictionary containing processing statistics

    Returns:
        Dictionary with results from each platform
    """
    print("\n" + "=" * 70)
    print("SOCIAL MEDIA UPDATE - Posting Work Summary")
    print("=" * 70)

    # Create summary message
    emails_processed = stats.get('emails_processed', 0)
    customers_added = stats.get('customers_added', 0)

    summary_message = f"Today our AI Employee processed {emails_processed} emails and added {customers_added} customers to Odoo! 🚀 #AI #Automation #Productivity"

    results = {
        'facebook': None,
        'instagram': None,
        'twitter': None,
        'linkedin': None,
        'errors': []
    }

    # Post to Facebook
    print("\n1. Posting to Facebook...")
    try:
        fb_result = post_to_facebook(summary_message)
        results['facebook'] = fb_result
        audit.log_social_media_post(
            platform='facebook',
            post_id=fb_result['post_id'],
            message=summary_message
        )
        print(f"   ✓ Facebook Post ID: {fb_result['post_id']}")
    except Exception as e:
        error_msg = str(e)
        results['errors'].append({'platform': 'facebook', 'error': error_msg})
        audit.log_social_media_post_failed(
            platform='facebook',
            error=error_msg,
            message=summary_message
        )
        print(f"   ✗ Facebook post failed: {error_msg}")

    # Post to Instagram (with a mock image path)
    print("\n2. Posting to Instagram...")
    try:
        ig_caption = f"Productivity boost! 📊 Our AI Employee handled {emails_processed} emails and onboarded {customers_added} new customers today! 💼 #BusinessGrowth #AI #Innovation"
        ig_result = post_to_instagram(
            image_path="images/ai_employee_work.jpg",
            caption=ig_caption
        )
        results['instagram'] = ig_result
        audit.log_social_media_post(
            platform='instagram',
            post_id=ig_result['post_id'],
            message=ig_caption
        )
        print(f"   ✓ Instagram Post ID: {ig_result['post_id']}")
    except Exception as e:
        error_msg = str(e)
        results['errors'].append({'platform': 'instagram', 'error': error_msg})
        audit.log_social_media_post_failed(
            platform='instagram',
            error=error_msg,
            message=summary_message
        )
        print(f"   ✗ Instagram post failed: {error_msg}")

    # Post to Twitter
    print("\n3. Posting to Twitter...")
    try:
        # Twitter has 280 char limit, so create a shorter message
        tweet_text = f"🤖 AI Employee Update: Processed {emails_processed} emails & added {customers_added} customers to Odoo today! #AI #Automation #BusinessGrowth"
        tw_result = post_to_twitter(tweet_text)
        results['twitter'] = tw_result
        audit.log_social_media_post(
            platform='twitter',
            post_id=tw_result['post_id'],
            message=tweet_text
        )
        print(f"   ✓ Twitter Post ID: {tw_result['post_id']}")
    except Exception as e:
        error_msg = str(e)
        results['errors'].append({'platform': 'twitter', 'error': error_msg})
        audit.log_social_media_post_failed(
            platform='twitter',
            error=error_msg,
            message=summary_message
        )
        print(f"   ✗ Twitter post failed: {error_msg}")

    # Post to LinkedIn (REAL-TIME DIRECT POSTING with Safety Guardrails)
    print("\n4. Posting to LinkedIn (Real-Time Direct Posting with Safety Guardrails)...")
    try:
        # Generate the LinkedIn-specific summary message
        linkedin_message = generate_linkedin_summary(emails_processed, customers_added)
        print(f"   Message: {linkedin_message}")

        linkedin_result = post_to_linkedin(
            message=linkedin_message,
            email_count=emails_processed,
            odoo_updates=customers_added
        )
        results['linkedin'] = linkedin_result

        # Handle different LinkedIn post statuses
        post_status = linkedin_result.get('status', '')
        
        if post_status == 'published':
            audit.log_linkedin_post(
                post_id=linkedin_result['post_id'],
                message=linkedin_message,
                email_count=emails_processed,
                odoo_updates=customers_added
            )
            print(f"   ✓ LinkedIn Post ID: {linkedin_result['post_id']}")
            print(f"   ✓ Post published LIVE on LinkedIn!")
        elif post_status == 'skipped_safety_limit':
            # Daily limit reached - safety guardrail activated
            audit.log(
                event_type="linkedin_post_skipped",
                status="skipped",
                details={
                    "reason": "daily_limit_reached",
                    "message": linkedin_message,
                    "daily_count": linkedin_result.get('daily_count', 0),
                    "max_posts": linkedin_result.get('max_posts', 2),
                    "safety_guardrail": True
                }
            )
            print(f"   ⚠️  Daily LinkedIn limit reached. Post skipped for safety.")
            print(f"      (Posts today: {linkedin_result.get('daily_count', 0)}/{linkedin_result.get('max_posts', 2)})")
        elif post_status == 'saved_for_manual_posting':
            # Fallback mode - saved to file
            audit.log(
                event_type="linkedin_post_saved",
                status="success",
                details={
                    "post_id": linkedin_result['post_id'],
                    "message": linkedin_message,
                    "filepath": linkedin_result.get('filepath', 'N/A')
                }
            )
            print(f"   ⚠️  Post saved for manual posting: {linkedin_result.get('filepath', 'N/A')}")
        else:
            # Unknown status
            print(f"   ⚠️  LinkedIn post status: {post_status}")
    except Exception as e:
        error_msg = str(e)
        results['errors'].append({'platform': 'linkedin', 'error': error_msg})
        audit.log_linkedin_post_failed(
            error=error_msg,
            message=generate_linkedin_summary(emails_processed, customers_added)
        )
        print(f"   ✗ LinkedIn post failed: {error_msg}")

    # Log social media campaign completion
    successful_posts = sum(1 for v in [results['facebook'], results['instagram'], results['twitter'], results['linkedin']] if v is not None and isinstance(v, dict) and v.get('status') == 'published')
    audit.log(
        event_type="social_media_campaign_completed",
        status="success" if successful_posts > 0 else "error",
        details={
            "successful_posts": successful_posts,
            "failed_posts": len(results['errors']),
            "platforms_posted": [k for k, v in results.items() if k != 'errors' and v is not None and isinstance(v, dict) and v.get('status') == 'published']
        }
    )

    print("\n" + "-" * 70)
    print(f"Social media update complete: {successful_posts}/4 posts successful")

    return results


def ceo_summary(stats: Dict[str, int]):
    """
    Print CEO Summary of the Ralph Wiggum Loop execution
    
    Args:
        stats: Dictionary containing processing statistics
    """
    print("\n" + "=" * 70)
    print("CEO SUMMARY")
    print("=" * 70)
    print(f"Today I processed {stats['emails_processed']} emails and added {stats['customers_added']} new customers to Odoo.")
    print("-" * 70)
    print(f"Detailed Statistics:")
    print(f"  • Total emails processed: {stats['emails_processed']}")
    print(f"  • Complex emails (needs action): {stats['complex_emails']}")
    print(f"  • Existing customers found: {stats['existing_customers']}")
    print(f"  • New customers added: {stats['customers_added']}")
    print(f"  • Errors encountered: {stats['errors']}")
    print("=" * 70)


def main():
    """Main entry point for the autonomous agent"""
    # Initialize audit logger
    audit = AuditLogger()

    logger.info("Starting Ralph Wiggum Loop autonomous agent")

    # Check critical background services (Heartbeat, Gmail Watcher)
    logger.info("Checking critical background services...")
    services_healthy = check_critical_services(audit)
    if not services_healthy:
        logger.error("CRITICAL: Executive Service Down - One or more background services have failed")

    try:
        # Execute the Ralph Wiggum Loop
        stats = ralph_wiggum_loop(audit)

        # Print CEO Summary
        ceo_summary(stats)

        logger.info(f"Ralph Wiggum Loop completed: {stats['emails_processed']} emails, {stats['customers_added']} new customers")

        # Post work summary to social media platforms
        social_results = post_work_summary_to_social_media(audit, stats)

        return stats, social_results

    except Exception as e:
        logger.error(f"Ralph Wiggum Loop failed: {e}")
        audit.log(
            event_type="ralph_wiggum_loop_error",
            status="error",
            details={"error": str(e)}
        )
        raise


if __name__ == '__main__':
    main()
