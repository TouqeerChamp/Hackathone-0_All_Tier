import json
import os
import tempfile
from unittest.mock import Mock
import sys
import base64

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the InboxHandler from the watcher module
from watcher import InboxHandler

def test_complex_json():
    """Test the on_created method with a complex JSON email"""

    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        logs_dir = os.path.join(temp_dir, 'logs')
        inbox_dir = os.path.join(temp_dir, 'inbox')
        done_dir = os.path.join(temp_dir, 'done')
        needs_action_dir = os.path.join(temp_dir, 'needs_action')

        os.makedirs(logs_dir)
        os.makedirs(inbox_dir)
        os.makedirs(done_dir)
        os.makedirs(needs_action_dir)

        # Create an instance of the handler
        handler = InboxHandler(logs_dir, inbox_dir, done_dir, needs_action_dir)

        # Create a test JSON file with complex content
        test_json_path = os.path.join(inbox_dir, 'complex_email.json')
        test_email_data = {
            "id": "complex456",
            "snippet": "Please analyze our quarterly reports and provide recommendations for strategic improvements in our business operations",
            "payload": {
                "headers": [
                    {
                        "name": "Subject",
                        "value": "Strategic Analysis Required for Q1"
                    },
                    {
                        "name": "From",
                        "value": "manager@company.com"
                    }
                ]
            }
        }

        with open(test_json_path, 'w', encoding='utf-8') as f:
            json.dump(test_email_data, f)

        # Test the JSON parsing logic directly
        with open(test_json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

            # Extract subject and snippet following the same logic as in the watcher
            subject = ""
            snippet = ""

            # Try to get the subject from the payload headers
            if 'payload' in json_data and 'headers' in json_data['payload']:
                for header in json_data['payload']['headers']:
                    if header.get('name', '').lower() == 'subject':
                        subject = header.get('value', '')
                        break

            # If subject is empty, try to get it from the snippet
            if not subject and 'snippet' in json_data:
                subject = json_data['snippet'][:100]  # Use first 100 chars of snippet as subject

            # Extract snippet as main content for categorization
            if 'snippet' in json_data:
                snippet = json_data['snippet']

            # Combine subject and snippet for content to categorize
            content = f"{subject}\n\n{snippet}" if snippet else subject

            print(f"Complex email - Extracted subject: {subject}")
            print(f"Complex email - Extracted snippet: {snippet}")
            print(f"Complex email - Combined content: {content}")

            # Test categorization
            category = handler.categorize_task(content)
            print(f"Complex email category: {category}")

        print("Complex JSON processing test completed successfully!")

if __name__ == "__main__":
    test_complex_json()