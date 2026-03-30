# Agent Skills Documentation

This document outlines the agent skills available and how to use them.

## Available Agent Skills

### Skill 1: Inbox Monitoring
- **Description**: Ability to scan the /inbox folder
- **Capability**: Monitor and list contents of the inbox folder to identify pending tasks

### Skill 2: Task Categorization
- **Description**: Ability to read file content and distinguish between 'simple' and 'complex' tasks
- **Capability**: Analyze task files and categorize them based on complexity for appropriate handling

### Skill 3: Dashboard Management
- **Description**: Ability to update Dashboard.md with current folder counts
- **Capability**: Maintain and update dashboard statistics for folder contents

### Skill 4: CEO Reporting
- **Description**: Ability to run briefing.py and generate summaries
- **Capability**: Generate executive summaries and reports when requested

## Instructions

When you ask the agent to 'process the inbox', the following sequence of skills will be executed:

1. **Inbox Monitoring**: Scan the /inbox folder to identify all pending tasks
2. **Task Categorization**: Read each task file and categorize as 'simple' or 'complex'
3. **Dashboard Management**: Update Dashboard.md with current folder counts
4. **CEO Reporting**: Run briefing.py to generate a summary of the processing

This sequence ensures that all incoming tasks are properly monitored, categorized, tracked, and reported on in a systematic manner.