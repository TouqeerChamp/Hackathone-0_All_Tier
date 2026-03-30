import os
import re
import time
from datetime import datetime

def process_files_immediately():
    """Process any files currently in inbox"""
    logs_dir = 'logs'
    inbox_dir = 'inbox'
    done_dir = 'done'
    needs_action_dir = 'needs_action'

    # Create all directories if they don't exist
    os.makedirs(logs_dir, exist_ok=True)
    os.makedirs(inbox_dir, exist_ok=True)
    os.makedirs(done_dir, exist_ok=True)
    os.makedirs(needs_action_dir, exist_ok=True)

    # Get all files from inbox
    inbox_files = [f for f in os.listdir(inbox_dir) if f.endswith(('.txt', '.md'))]

    for filename in inbox_files:
        filepath = os.path.join(inbox_dir, filename)
        print(f'Processing: {filename}')

        # Read the content of the file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f'File content: {repr(content[:100])}...')
        except Exception as e:
            print(f'Error reading file: {e}')
            continue

        # Categorize the task with our updated logic
        category = categorize_task(content)
        print(f'Task categorized as: {category}')

        # Move the file based on category
        if category == 'simple':
            destination = os.path.join(done_dir, filename)
            print(f'Moving {filename} to done/')
        else:  # complex
            destination = os.path.join(needs_action_dir, filename)
            print(f'Moving {filename} to needs_action/')

        # Move the file
        os.rename(filepath, destination)

        # Update the dashboard
        update_dashboard(inbox_dir, needs_action_dir, done_dir, logs_dir)
        print(f'Dashboard updated after processing {filename}')

        # Create log entry
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f'[{timestamp}] New file processed: {filename} (categorized as {category})\n'

        log_file_path = os.path.join(logs_dir, 'activity.log')
        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(log_entry)

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

    # Check for Urdu script (Unicode ranges for Arabic/Persian characters used in Urdu)
    has_urdu_script = any('\u0600' <= char <= '\u06FF' for char in content)

    # Check for Roman Urdu patterns (common Urdu words written in Latin script)
    roman_urdu_patterns = ['kaise', 'kya', 'hai', 'ke', 'ka', 'ki', 'na', 'kar', 'ho', 'ay']
    has_roman_urdu = any(pattern in content.lower() for pattern in roman_urdu_patterns)

    print(f'Content: {repr(content)}')
    print(f'Has Urdu script: {has_urdu_script}')
    print(f'Has Roman Urdu: {has_roman_urdu}')

    # Check for simple indicators with word boundaries
    for indicator in simple_indicators:
        pattern = r'\b' + re.escape(indicator) + r'\b'
        if re.search(pattern, content.lower()):
            print(f'Found simple indicator: {indicator}')
            return 'simple'

    # Check for complex indicators with word boundaries
    for indicator in complex_indicators:
        pattern = r'\b' + re.escape(indicator) + r'\b'
        if re.search(pattern, content.lower()):
            print(f'Found complex indicator: {indicator}')
            return 'complex'

    # If contains Urdu script or Roman Urdu patterns, categorize as complex (likely needs human understanding)
    if has_urdu_script or has_roman_urdu:
        print('Has Urdu script or Roman Urdu patterns - returning complex')
        return 'complex'

    # If content is very short, consider it simple
    if len(content) < 20:
        return 'simple'

    # Default to complex if uncertain
    return 'complex'

def update_dashboard(inbox_dir, needs_action_dir, done_dir, logs_dir):
    """Update Dashboard.md with current folder counts"""
    inbox_count = len([f for f in os.listdir(inbox_dir) if os.path.isfile(os.path.join(inbox_dir, f))])
    needs_action_count = len([f for f in os.listdir(needs_action_dir) if os.path.isfile(os.path.join(needs_action_dir, f))])
    done_count = len([f for f in os.listdir(done_dir) if os.path.isfile(os.path.join(done_dir, f))])
    logs_count = len([f for f in os.listdir(logs_dir) if os.path.isfile(os.path.join(logs_dir, f))])

    # Create the updated dashboard content
    dashboard_content = f'''# AI Employee Dashboard

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
'''

    # Determine status indicators
    inbox_status = '⚠️ Processing' if inbox_count > 0 else '✅ Ready'
    needs_action_status = '⚠️ Processing' if needs_action_count > 0 else '✅ Ready'
    done_status = '✅ Ready' if done_count > 0 else '✅ Ready'
    logs_status = '✅ Ready' if logs_count > 0 else '✅ Ready'

    # Replace placeholders with actual status indicators
    dashboard_content = dashboard_content.replace('{inbox_status}', inbox_status)
    dashboard_content = dashboard_content.replace('{needs_action_status}', needs_action_status)
    dashboard_content = dashboard_content.replace('{done_status}', done_status)
    dashboard_content = dashboard_content.replace('{logs_status}', logs_status)

    # Write the updated dashboard
    with open('Dashboard.md', 'w', encoding='utf-8') as f:
        f.write(dashboard_content)

if __name__ == '__main__':
    print('Processing inbox files...')
    process_files_immediately()
    print('Processing complete.')