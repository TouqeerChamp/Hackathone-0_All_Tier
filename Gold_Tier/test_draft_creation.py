#!/usr/bin/env python3
"""
Test script to validate the draft creation functionality in gmail_watcher.py
"""

import json
import os
from gmail_watcher import authenticate_gmail, create_draft

def test_draft_creation():
    """Test the create_draft function with a sample email file"""
    print("Testing draft creation functionality...")

    # Look for a sample email JSON file
    sample_email_path = None
    for dir_name in ['done', 'needs_action', 'inbox']:
        if os.path.exists(dir_name):
            for file_name in os.listdir(dir_name):
                if file_name.endswith('.json'):
                    sample_email_path = os.path.join(dir_name, file_name)
                    break
        if sample_email_path:
            break

    if not sample_email_path:
        print("No email JSON files found to test with.")
        print("Creating a sample email data structure for testing...")

        # Create a sample email data structure
        sample_email_data = {
            "id": "test_message_id_12345",
            "payload": {
                "headers": [
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "To", "value": "recipient@example.com"}
                ],
                "body": {
                    "data": "VGVzdCBtZXNzYWdlIGJvZHk="  # Base64 encoded "Test message body"
                }
            }
        }

        print(f"Using sample email data for testing: {sample_email_data['id']}")
    else:
        print(f"Using sample email file: {sample_email_path}")
        with open(sample_email_path, 'r', encoding='utf-8') as f:
            sample_email_data = json.load(f)

    # Authenticate to Gmail
    try:
        print("Authenticating to Gmail...")
        service = authenticate_gmail()
        print("Authentication successful!")

        # Test the draft creation
        reply_text = "Thank you for your message. This is an automated response confirming that your request has been received and processed. If you need any further assistance, please feel free to contact us."

        print("Creating draft reply...")
        draft = create_draft(service, sample_email_data, reply_text)

        if draft:
            print(f"Draft created successfully! Draft ID: {draft.get('id', 'Unknown')}")
        else:
            print("Draft creation failed.")

    except Exception as e:
        print(f"Error during draft creation: {e}")
        print("Note: If this is the first time running, you may need to authenticate through the browser.")

if __name__ == "__main__":
    test_draft_creation()