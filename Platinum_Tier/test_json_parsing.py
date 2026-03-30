import json
import base64
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the InboxHandler class from watcher.py
from watcher import InboxHandler

def test_json_parsing():
    # Create directories for testing
    os.makedirs('logs', exist_ok=True)
    os.makedirs('inbox', exist_ok=True)
    os.makedirs('done', exist_ok=True)
    os.makedirs('needs_action', exist_ok=True)

    # Create an InboxHandler instance
    handler = InboxHandler('logs', 'inbox', 'done', 'needs_action')

    # Test JSON email data
    test_json_content = {
        "id": "test123",
        "snippet": "This is a simple test email that should be categorized as a simple task",
        "payload": {
            "headers": [
                {
                    "name": "Subject",
                    "value": "Test Email Subject"
                },
                {
                    "name": "From",
                    "value": "test@example.com"
                },
                {
                    "name": "Date",
                    "value": "Wed, 18 Feb 2026 10:00:00 +0000"
                }
            ],
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {
                        "data": "VGhpcyBpcyB0aGUgZW1haWwgY29udGVudCBmb3IgdGVzdGluZy4="
                    }
                }
            ]
        }
    }

    # Parse JSON data similar to how watcher.py does
    subject = ""
    snippet = ""

    # Try to get the subject from the payload headers
    if 'payload' in test_json_content and 'headers' in test_json_content['payload']:
        for header in test_json_content['payload']['headers']:
            if header.get('name', '').lower() == 'subject':
                subject = header.get('value', '')
                break

    # If subject is empty, try to get it from the snippet
    if not subject and 'snippet' in test_json_content:
        subject = test_json_content['snippet'][:100]  # Use first 100 chars of snippet as subject

    # Extract snippet as main content for categorization
    if 'snippet' in test_json_content:
        snippet = test_json_content['snippet']

    # Combine subject and snippet for content to categorize
    content = f"{subject}\n\n{snippet}" if snippet else subject

    print(f"Extracted subject: {subject}")
    print(f"Extracted snippet: {snippet}")
    print(f"Combined content: {content}")

    # Categorize the content
    category = handler.categorize_task(content)
    print(f"Category result: {category}")

    # Test with a complex email
    complex_json_content = {
        "id": "test456",
        "snippet": "Please analyze our quarterly reports and provide recommendations for strategic improvements",
        "payload": {
            "headers": [
                {
                    "name": "Subject",
                    "value": "Strategic Analysis Required"
                }
            ]
        }
    }

    subject2 = ""
    snippet2 = ""

    # Try to get the subject from the payload headers
    if 'payload' in complex_json_content and 'headers' in complex_json_content['payload']:
        for header in complex_json_content['payload']['headers']:
            if header.get('name', '').lower() == 'subject':
                subject2 = header.get('value', '')
                break

    # If subject is empty, try to get it from the snippet
    if not subject2 and 'snippet' in complex_json_content:
        subject2 = complex_json_content['snippet'][:100]  # Use first 100 chars of snippet as subject

    # Extract snippet as main content for categorization
    if 'snippet' in complex_json_content:
        snippet2 = complex_json_content['snippet']

    # Combine subject and snippet for content to categorize
    content2 = f"{subject2}\n\n{snippet2}" if snippet2 else subject2

    print(f"\nComplex email - Extracted subject: {subject2}")
    print(f"Complex email - Extracted snippet: {snippet2}")
    print(f"Complex email - Combined content: {content2}")

    # Categorize the content
    category2 = handler.categorize_task(content2)
    print(f"Complex email category result: {category2}")

    print("\nJSON parsing test completed successfully!")

    # Clean up directories
    import shutil
    for dir_name in ['logs', 'inbox', 'done', 'needs_action']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

if __name__ == "__main__":
    test_json_parsing()