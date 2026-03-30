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
from typing import Dict, List, Any, Optional, Tuple

# Enable UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Import local modules
from inbox_scanner import scan_inbox, process_email_file, categorize_task
from odoo_client import get_odoo_connection, execute_odoo_query, ODOO_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AutonomousAgent")

# Constants
AUDIT_LOG_DIR = "logs/audit_logs"
INBOX_DIR = "inbox"


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
    
    try:
        # Execute the Ralph Wiggum Loop
        stats = ralph_wiggum_loop(audit)
        
        # Print CEO Summary
        ceo_summary(stats)
        
        logger.info(f"Ralph Wiggum Loop completed: {stats['emails_processed']} emails, {stats['customers_added']} new customers")
        
        return stats
        
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
