import os
import re
from datetime import datetime
from pathlib import Path

def generate_briefing():
    """
    Generate a CEO briefing based on logs and dashboard data
    """
    # Define file paths
    activity_log_path = "logs/activity.log"
    dashboard_path = "Dashboard.md"
    needs_action_dir = "needs_action"

    # Create timestamp for the briefing filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    briefing_filename = f"CEO_Briefing_{timestamp}.md"
    briefing_path = f"logs/{briefing_filename}"

    # Initialize counters
    total_tasks = 0
    simple_tasks = 0
    complex_tasks = 0

    # Read the activity log to count tasks
    if os.path.exists(activity_log_path):
        with open(activity_log_path, 'r', encoding='utf-8') as log_file:
            log_content = log_file.read()

        # Count total tasks processed today
        # Log format: [YYYY-MM-DD HH:MM:SS] New file detected: filename (categorized as simple|complex)
        # Look for entries that indicate task categorization
        today_date = datetime.now().strftime("%Y-%m-%d")

        # Find entries with categorization (simple or complex)
        categorized_entries = re.findall(rf'\[{today_date}.*?\] New file detected:.*?\(categorized as (simple|complex)\)', log_content)
        total_tasks = len(categorized_entries)
        simple_tasks = categorized_entries.count('simple')
        complex_tasks = categorized_entries.count('complex')
    else:
        print(f"Warning: {activity_log_path} not found")

    # Read dashboard content (if exists)
    dashboard_content = ""
    if os.path.exists(dashboard_path):
        with open(dashboard_path, 'r', encoding='utf-8') as dashboard_file:
            dashboard_content = dashboard_file.read()

    # Get list of files in needs_action directory
    needs_action_files = []
    if os.path.exists(needs_action_dir) and os.path.isdir(needs_action_dir):
        needs_action_files = os.listdir(needs_action_dir)
    else:
        print(f"Warning: {needs_action_dir} directory not found")

    # Generate the briefing content
    briefing_content = f"""# CEO Briefing - {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

## Task Summary

- **Total tasks processed today:** {total_tasks}
- **Simple tasks:** {simple_tasks}
- **Complex tasks:** {complex_tasks}

## Needs Action

The following files require your attention:

"""

    if needs_action_files:
        for filename in needs_action_files:
            briefing_content += f"- {filename}\n"
    else:
        briefing_content += "- No files currently need action\n"

    briefing_content += "\n## Dashboard Summary\n\n"
    briefing_content += dashboard_content if dashboard_content else "No dashboard content available."

    # Write the briefing to the file
    os.makedirs("logs", exist_ok=True)  # Ensure logs directory exists
    with open(briefing_path, 'w', encoding='utf-8') as briefing_file:
        briefing_file.write(briefing_content)

    print(f"CEO Briefing generated: {briefing_path}")
    return briefing_path

if __name__ == "__main__":
    generate_briefing()