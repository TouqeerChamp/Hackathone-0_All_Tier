import os
import re
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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
        content_lower = content.lower().strip()

        # Simple tasks that can be done automatically
        simple_indicators = [
            'hello', 'hi', 'greet', 'test', 'update log', 'note', 'log',
            'simple', 'easy', 'trivial', 'basic', 'update', 'record', 'write',
            'create', 'make', 'add', 'hello world', 'say hello'
        ]

        # Complex tasks that need human input
        complex_indicators = [
            'analyze', 'research', 'think about', 'consider', 'review',
            'evaluate', 'summarize', 'opinion', 'advice', 'help', 'how',
            'why', 'what do you think', 'suggest', 'recommend', 'strategy',
            'complex', 'difficult', 'challenging', 'important decision',
            'question', 'inquiry', 'information', 'learn', 'explain',
            'understand', 'investigate', 'plan', 'design', 'create proposal'
        ]

        # Check for simple indicators
        for indicator in simple_indicators:
            if indicator in content_lower:
                return "simple"

        # Check for complex indicators
        for indicator in complex_indicators:
            if indicator in content_lower:
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

    def on_created(self, event):
        # Only process .txt and .md files
        if not event.is_directory and (event.src_path.endswith('.txt') or event.src_path.endswith('.md')):
            filename = os.path.basename(event.src_path)
            print(f'New file detected: {filename}')

            # Read the content of the file
            try:
                with open(event.src_path, 'r', encoding='utf-8') as f:
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
                destination = os.path.join(self.done_dir, filename)
                print(f'Moving {filename} to done/')
            else:  # complex
                destination = os.path.join(self.needs_action_dir, filename)
                print(f'Moving {filename} to needs_action/')

            # Move the file
            os.rename(event.src_path, destination)

            # Update the dashboard
            self.update_dashboard()
            print(f'Dashboard updated after processing {filename}')

            # Create log entry
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f'[{timestamp}] New file detected: {filename} (categorized as {category})\n'

            log_file_path = os.path.join(self.logs_dir, 'activity.log')
            with open(log_file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(log_entry)

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