import os
import re
import time
import shutil
import json
import base64
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Import the Gmail functions
from gmail_watcher import authenticate_gmail, create_draft

class InboxHandler(FileSystemEventHandler):
    def __init__(self, logs_dir, inbox_dir, done_dir, needs_action_dir):
        self.logs_dir = logs_dir
        self.inbox_dir = inbox_dir
        self.done_dir = done_dir
        self.needs_action_dir = needs_action_dir
        # Create logs directory if it doesn't exist
        os.makedirs(logs_dir, exist_ok=True)

    def categorize_task(self, content):
        """Use reasoning to categorize the task based on content"""
        import re

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

        # Check for Urdu script (Unicode ranges for Arabic/Persian characters used in Urdu)
        has_urdu_script = any('\u0600' <= char <= '\u06FF' for char in content)

        # Check for Roman Urdu patterns (common Urdu words written in Latin script)
        roman_urdu_patterns = ['kaise', 'kya', 'hai', 'ke', 'ka', 'ki', 'na', 'kar', 'ho', 'ay']
        has_roman_urdu = any(pattern in content.lower() for pattern in roman_urdu_patterns)

        # Create regex patterns for word boundaries to avoid substring matches
        # Check for simple indicators with word boundaries
        for indicator in simple_indicators:
            pattern = r'\b' + re.escape(indicator) + r'\b'
            if re.search(pattern, content.lower()):
                return "simple"

        # Check for complex indicators with word boundaries
        for indicator in complex_indicators:
            pattern = r'\b' + re.escape(indicator) + r'\b'
            if re.search(pattern, content.lower()):
                return "complex"

        # If contains Urdu script or Roman Urdu patterns, categorize as complex (likely needs human understanding)
        if has_urdu_script or has_roman_urdu:
            return "complex"

        # If content is very short, consider it simple
        if len(content) < 20:
            return "simple"

        # Default to complex if uncertain
        return "complex"

    def update_dashboard(self):
        """Update Dashboard.md with current folder counts"""
        inbox_count = len([f for f in os.listdir(self.inbox_dir) if os.path.isfile(os.path.join(self.inbox_dir, f))])
        needs_action_count = len([f for f in os.listdir(self.needs_action_dir) if os.path.isfile(os.path.join(self.needs_action_dir, f))])
        done_count = len([f for f in os.listdir(self.done_dir) if os.path.isfile(os.path.join(self.done_dir, f))])
        logs_count = len([f for f in os.listdir(self.logs_dir) if os.path.isfile(os.path.join(self.logs_dir, f))])

        # Create the updated dashboard content
        dashboard_content = f"""# AI Employee Dashboard

## Folder Status Overview

| Folder | Status | Count | Description |
|--------|--------|-------|-------------|
| 📥 **Inbox** | {{inbox_status}} | {inbox_count} | Contains new items requiring action |
| ⚡ **Needs Action** | {{needs_action_status}} | {needs_action_count} | Items that require processing |
| ✅ **Done** | {{done_status}} | {done_count} | Completed tasks and activities |
| 📝 **Logs** | {{logs_status}} | {logs_count} | System logs and activity records |

## Current System Status

- **AI Employee Role**: Digital Operations Assistant
- **Primary Function**: Monitor and process inbox items
- **Folders Initialized**: 4/4 folders operational
- **Workflows**: Ready to process tasks

## Next Steps

1. Monitor inbox for new incoming items
2. Process items according to priority
3. Update status as tasks move through the system
"""

        # Determine status indicators
        inbox_status = "⚠️ Processing" if inbox_count > 0 else "✅ Ready"
        needs_action_status = "⚠️ Processing" if needs_action_count > 0 else "✅ Ready"
        done_status = "✅ Ready" if done_count > 0 else "✅ Ready"
        logs_status = "✅ Ready" if logs_count > 0 else "✅ Ready"

        # Replace placeholders with actual status indicators
        dashboard_content = dashboard_content.replace("{inbox_status}", inbox_status)
        dashboard_content = dashboard_content.replace("{needs_action_status}", needs_action_status)
        dashboard_content = dashboard_content.replace("{done_status}", done_status)
        dashboard_content = dashboard_content.replace("{logs_status}", logs_status)

        # Write the updated dashboard
        with open('Dashboard.md', 'w', encoding='utf-8') as f:
            f.write(dashboard_content)

    def process_file(self, file_path):
        """Process a single file based on its content"""
        filename = os.path.basename(file_path)
        print(f'Processing file: {filename}')

        # Read the content of the file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    # Parse JSON file
                    json_data = json.load(f)

                    # Extract subject and snippet from the JSON
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

                else:
                    # For .txt and .md files, read normally
                    content = f.read()

            print(f'File content: {content[:100]}...')  # Print first 100 chars
        except Exception as e:
            print(f'Error reading file: {e}')
            return

        # Categorize the task
        category = self.categorize_task(content)
        print(f'Task categorized as: {category}')

        # Move the file based on category
        if category == "simple":
            destination_dir = self.done_dir
            print(f'Moving {filename} to done/')

            # If this is an email JSON file, create a draft reply
            if file_path.endswith('.json'):
                try:
                    # Load the email data from the file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        original_email_data = json.load(f)

                    # Create a polite AI-generated response
                    reply_text = "Thank you for your message. This is an automated response confirming that your request has been received and processed. If you need any further assistance, please feel free to contact us."

                    # Authenticate and get Gmail service
                    service = authenticate_gmail()

                    # Create a draft reply
                    create_draft(service, original_email_data, reply_text)

                except Exception as e:
                    print(f'Error creating draft reply: {e}')
        else:  # complex
            destination_dir = self.needs_action_dir
            print(f'Moving {filename} to needs_action/')

        # Create destination path
        destination = os.path.join(destination_dir, filename)

        # Handle case where destination file already exists
        if os.path.exists(destination):
            # Get file extension and name without extension
            name, ext = os.path.splitext(filename)
            # Create a timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Include milliseconds for uniqueness
            # Create new filename with timestamp
            new_filename = f"{name}_{timestamp}{ext}"
            destination = os.path.join(destination_dir, new_filename)
            print(f'Destination file already exists. Renaming to: {new_filename}')

        # Move the file
        shutil.move(file_path, destination)

        # Update the dashboard
        self.update_dashboard()
        print(f'Dashboard updated after processing {filename}')

        # Create log entry
        destination_filename = os.path.basename(destination)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f'[{timestamp}] File processed: {filename} -> {destination_filename} (categorized as {category})\n'

        log_file_path = os.path.join(self.logs_dir, 'activity.log')
        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(log_entry)

    def process_existing_files(self):
        """Process all existing files in the inbox folder"""
        inbox_files = []
        for file_name in os.listdir(self.inbox_dir):
            file_path = os.path.join(self.inbox_dir, file_name)
            if os.path.isfile(file_path) and (file_name.endswith('.txt') or file_name.endswith('.md') or file_name.endswith('.json')):
                inbox_files.append(file_path)

        print(f'Found {len(inbox_files)} existing files in inbox to process')

        for file_path in inbox_files:
            self.process_file(file_path)

    def on_created(self, event):
        # Process .txt, .md, and .json files
        if not event.is_directory and (event.src_path.endswith('.txt') or event.src_path.endswith('.md') or event.src_path.endswith('.json')):
            self.process_file(event.src_path)

def main():
    # Define folder paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    inbox_dir = os.path.join(current_dir, 'inbox')
    logs_dir = os.path.join(current_dir, 'logs')
    done_dir = os.path.join(current_dir, 'done')
    needs_action_dir = os.path.join(current_dir, 'needs_action')

    # Create all directories if they don't exist
    os.makedirs(inbox_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)
    os.makedirs(done_dir, exist_ok=True)
    os.makedirs(needs_action_dir, exist_ok=True)

    # Create the event handler
    event_handler = InboxHandler(logs_dir, inbox_dir, done_dir, needs_action_dir)

    # Process any existing files in the inbox first
    print('Scanning inbox for existing files...')
    event_handler.process_existing_files()

    # Create the observer
    observer = Observer()
    observer.schedule(event_handler, inbox_dir, recursive=False)

    # Start the observer
    observer.start()
    print(f'Watching inbox folder: {inbox_dir}')
    print('Press Ctrl+C to stop.')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print('\nStopping file watcher...')

    observer.join()

if __name__ == '__main__':
    main()