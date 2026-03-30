"""
Inbox Scanner - One-time scan of inbox folder
=============================================
This script processes all existing files in the inbox folder once,
then exits. Used for batch/scheduled execution.
"""

import os
import sys
import re
import shutil
import json
from datetime import datetime

# Enable UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Import the Gmail functions
from gmail_watcher import authenticate_gmail, create_draft

def categorize_task(content):
    """Use reasoning to categorize the task based on content"""
    
    # Simple tasks that can be done automatically
    simple_indicators = [
        'hello', 'hi', 'greet', 'test', 'update log', 'note', 'log',
        'simple', 'easy', 'trivial', 'basic', 'update', 'record', 'write',
        'create', 'make', 'add', 'hello world', 'say hello',
        'salam', 'kaam khatam', 'shukriya', 'theek hai'
    ]

    # Complex tasks that need human input
    complex_indicators = [
        'analyze', 'research', 'think about', 'consider', 'review',
        'evaluate', 'summarize', 'opinion', 'advice', 'help', 'how',
        'why', 'what do you think', 'suggest', 'recommend', 'strategy',
        'complex', 'difficult', 'challenging', 'important decision',
        'question', 'inquiry', 'information', 'learn', 'explain',
        'understand', 'investigate', 'plan', 'design', 'create proposal',
        'socho', 'mashwara', 'batao', 'khulasa'
    ]

    # Check for Urdu script
    has_urdu_script = any('\u0600' <= char <= '\u06FF' for char in content)

    # Check for Roman Urdu patterns
    roman_urdu_patterns = ['kaise', 'kya', 'hai', 'ke', 'ka', 'ki', 'na', 'kar', 'ho', 'ay']
    has_roman_urdu = any(pattern in content.lower() for pattern in roman_urdu_patterns)

    content_lower = content.lower()

    simple_score = sum(1 for indicator in simple_indicators if indicator in content_lower)
    complex_score = sum(1 for indicator in complex_indicators if indicator in content_lower)

    if has_urdu_script or has_roman_urdu:
        complex_score += 2

    if complex_score > simple_score:
        return 'needs_action'
    else:
        return 'done'


def process_email_file(file_path):
    """Process a single email file and create a Gmail draft"""
    print(f"Processing: {os.path.basename(file_path)}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the JSON content
        email_data = json.loads(content)
        
        sender = email_data.get('from', {}).get('email', 'Unknown')
        subject = email_data.get('subject', 'No Subject')
        body = email_data.get('snippet', '')
        date = email_data.get('date', datetime.now().isoformat())
        
        # Check for Urdu and translate if needed
        has_urdu = any('\u0600' <= char <= '\u06FF' for char in body)
        if has_urdu:
            body = f"[Urdu content detected - translation requires API]\n\n{body}"
        
        # Categorize the task
        category = categorize_task(body)
        
        # Create the draft content
        draft_content = f"""
Task Details:
- From: {sender}
- Subject: {subject}
- Date: {date}
- Category: {category}

Message:
{body}

---
Processed by AI Employee on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        print(f"  Category: {category}")
        print(f"  Draft content created ({len(draft_content)} chars)")
        
        return True
        
    except Exception as e:
        print(f"  ERROR: {str(e)}")
        return False


def scan_inbox(inbox_dir='inbox', logs_dir='logs'):
    """Scan inbox directory and process all .json files"""
    print("=" * 60)
    print("INBOX SCANNER - One-time Scan")
    print("=" * 60)
    print(f"Scanning: {os.path.abspath(inbox_dir)}")
    print()
    
    if not os.path.exists(inbox_dir):
        print(f"Inbox directory not found: {inbox_dir}")
        return 0
    
    json_files = [f for f in os.listdir(inbox_dir) if f.endswith('.json')]
    
    if not json_files:
        print("No .json files found in inbox.")
        return 0
    
    print(f"Found {len(json_files)} file(s) to process")
    print("-" * 60)
    
    processed = 0
    for filename in json_files:
        file_path = os.path.join(inbox_dir, filename)
        if process_email_file(file_path):
            processed += 1
    
    print("-" * 60)
    print(f"Scan complete. Processed {processed}/{len(json_files)} files.")
    print("=" * 60)
    
    return processed


if __name__ == '__main__':
    scan_inbox()
