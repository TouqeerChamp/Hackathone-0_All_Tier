#!/usr/bin/env python3
"""
Process complex emails in needs_action folder and create Plan.md files based on research using Google Search MCP.
Gold Tier: Implements graceful degradation for MCP server failures.
"""
import json
import os
import base64
from pathlib import Path
import re
from typing import Dict, Any, List
import subprocess
import sys

# Import graceful degradation utilities
from graceful_degradation import GracefulDegradation, FallbackMethod

# Create a graceful degradation handler for Google Search MCP
google_search_degrader = GracefulDegradation(
    service_name="Google Search MCP",
    fallbacks=[
        FallbackMethod.LOCAL_CACHE,
        FallbackMethod.MANUAL_RESEARCH,
        FallbackMethod.SKIP_WITH_LOG
    ],
    cache_dir="logs/audit_logs/cache/google_search"
)


def decode_email_body(body_data: str) -> str:
    """Decode the base64 encoded email body."""
    try:
        # Add padding if needed
        missing_padding = len(body_data) % 4
        if missing_padding:
            body_data += '=' * (4 - missing_padding)

        decoded_bytes = base64.urlsafe_b64decode(body_data)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        print(f"Error decoding email body: {e}")
        return ""


def extract_email_content(email_file: str) -> Dict[str, Any]:
    """Extract content from an email JSON file."""
    with open(email_file, 'r', encoding='utf-8') as f:
        email_data = json.load(f)

    # Extract email metadata
    subject = ""
    body = ""

    # Get subject from headers
    if 'payload' in email_data and 'headers' in email_data['payload']:
        for header in email_data['payload']['headers']:
            if header.get('name', '').lower() == 'subject':
                subject = header.get('value', 'No Subject')
                break

    # Get body from parts
    if 'payload' in email_data and 'parts' in email_data['payload']:
        for part in email_data['payload']['parts']:
            if 'body' in part and 'data' in part['body']:
                body = decode_email_body(part['body']['data'])
                break
    elif 'payload' in email_data and 'body' in email_data['payload'] and 'data' in email_data['payload']['body']:
        body = decode_email_body(email_data['payload']['body']['data'])

    # If body is still empty, try to get from snippet
    if not body:
        body = email_data.get('snippet', '')

    return {
        'id': email_data.get('id', ''),
        'subject': subject,
        'body': body,
        'from': next((header['value'] for header in email_data.get('payload', {}).get('headers', [])
                     if header.get('name', '').lower() == 'from'), ''),
        'date': next((header['value'] for header in email_data.get('payload', {}).get('headers', [])
                     if header.get('name', '').lower() == 'date'), '')
    }


def google_search_mcp(query: str, num_results: int = 5) -> Dict[str, Any]:
    """
    Call the Google Search MCP service to perform a search.
    Implements graceful degradation with fallback methods.
    """
    try:
        # Prepare input data
        input_data = {
            "query": query,
            "num_results": num_results
        }

        # Call the MCP service
        result = subprocess.run([
            sys.executable,
            str(Path(".claude/mcp/google_search.py")),
            "google_search"
        ],
            input=json.dumps(input_data),
            text=True,
            capture_output=True,
            timeout=30
        )

        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode,
                "google_search.py",
                output=result.stdout,
                stderr=result.stderr
            )

        search_result = json.loads(result.stdout)
        
        # Check if the result contains an error
        if 'error' in search_result:
            raise Exception(search_result['error'])
        
        # Record success and cache the result
        google_search_degrader.record_success(search_result, query=query, num_results=num_results)
        
        return search_result
        
    except Exception as e:
        # Use graceful degradation to handle the failure
        fallback_result = google_search_degrader.handle_failure(
            error=e,
            original_function="google_search_mcp",
            query=query,
            num_results=num_results
        )
        
        # Return fallback result or a safe default
        if fallback_result is not None:
            return fallback_result
        
        return {
            "error": f"Google Search MCP failed and all fallbacks exhausted: {str(e)}",
            "fallback_applied": True
        }


def create_plan_for_email_with_research(email_content: Dict[str, Any]) -> str:
    """Create a Plan.md content for a complex email using Google Search research."""
    import time
    subject = email_content['subject']
    body = email_content['body']

    # Identify key research topics from the email
    key_topics = extract_key_topics(subject, body)

    # Perform Google searches for each key topic
    research_results = {}
    fallback_topics = []  # Track topics that used fallbacks
    
    for i, topic in enumerate(key_topics):
        print(f"Researching: {topic}")
        search_result = google_search_mcp(topic)
        
        # Check if fallback was applied
        if search_result.get('fallback_applied') or search_result.get('source') in ['cache', 'manual_research_template', 'skipped']:
            fallback_topics.append(topic)
            print(f"  ⚠ Fallback applied for: {topic}")
        
        if 'error' not in search_result or search_result.get('source'):
            research_results[topic] = search_result.get('results', search_result.get('data', []))
        else:
            research_results[topic] = [{"title": "Research Error", "link": "#", "snippet": search_result.get('error', 'Unknown error')}]

        # Add a small delay between searches to avoid rate limiting
        if i < len(key_topics) - 1:  # Don't delay after the last search
            time.sleep(1)

    # Create comprehensive plan
    plan_content = f"""# Plan for: {subject}

## Email Details
- **From**: {email_content['from']}
- **Date**: {email_content['date']}
- **Subject**: {subject}

## Summary
{body[:500]}{'...' if len(body) > 500 else ''}

## Key Topics Identified
"""

    for topic in key_topics:
        plan_content += f"- {topic}\n"

    # Add fallback notice if any topics used fallbacks
    if fallback_topics:
        plan_content += f"""
## ⚠ Service Degradation Notice
The following topics could not be researched due to service unavailability and used fallback methods:
"""
        for topic in fallback_topics:
            plan_content += f"- {topic}\n"
        plan_content += """
Please consider manual research for these topics if needed.

"""

    plan_content += "\n## Research Results\n"

    for topic, results in research_results.items():
        plan_content += f"\n### Research on '{topic}'\n"
        if not results:
            plan_content += "*No research results available.*\n"
            continue
            
        for i, result in enumerate(results, 1):
            # Handle different result formats (normal vs fallback)
            title = result.get('title', 'Untitled')
            link = result.get('link', '#')
            snippet = result.get('snippet', '')
            
            plan_content += f"**Result {i}**: [{title}]({link})\n"
            if snippet:
                plan_content += f"> {snippet}\n\n"

    plan_content += """## Analysis
Based on the research, the following observations can be made:

1. Key stakeholders and entities have been identified through research
2. Important contextual information has been gathered
3. Relevant resources and references are available

## Action Items
1. Review research results and identify actionable insights
2. Create a detailed response or action plan based on findings
3. Prioritize tasks based on the email's requirements
4. Update relevant documentation
5. Move email to 'done' folder after processing

## Next Steps
1. Synthesize research findings into actionable steps
2. Develop specific solutions or responses as needed
3. Follow up on any outstanding items
"""
    return plan_content


def extract_key_topics(subject: str, body: str) -> List[str]:
    """Extract key research topics from the email subject and body."""
    # Combine subject and body for analysis
    text = f"{subject} {body}"

    # Extract potential topics:
    # - Organizations/companies (capitalized words that might be company names)
    # - Job titles (positions mentioned)
    # - Important phrases related to jobs or tasks

    # Look for company names (sequences of capitalized words)
    companies = re.findall(r'\b[A-Z][A-Z]+\b(?:\s+[A-Z][a-z]+)*', text)
    companies = [c.strip() for c in companies if len(c) > 2 and c != "THE" and c != "AND"]

    # Look for job titles
    job_titles = re.findall(r'\b(?:[A-Z][a-z]*\s+)*[A-Z][a-z]*\s+Executive\b|\b(?:[A-Z][a-z]*\s+)*[A-Z][a-z]*\s+Manager\b|\b(?:[A-Z][a-z]*\s+)*[A-Z][a-z]*\s+Director\b|\b(?:[A-Z][a-z]*\s+)*[A-Z][a-z]*\s+Analyst\b|\b(?:[A-Z][a-z]*\s+)*[A-Z][a-z]*\s+Engineer\b|\b(?:[A-Z][a-z]*\s+)*[A-Z][a-z]*\s+Developer\b|\b(?:[A-Z][a-z]*\s+)*[A-Z][a-z]*\s+Specialist\b', text, re.IGNORECASE)

    # Extract location data
    locations = re.findall(r'\b(?:[A-Z][a-z]*\s*)+[A-Z][a-z]*\b', text)
    locations = [loc.strip() for loc in locations if 'Karachi' in loc or 'Gulshan' in loc or 'Pakistan' in loc or 'Lahore' in loc or 'Islamabad' in loc]

    # Combine all topics
    topics = list(set(companies + job_titles + locations))

    # Add the main subject as a topic
    topics.append(subject)

    # Filter out duplicates and return
    unique_topics = []
    for topic in topics:
        if topic and topic not in unique_topics and len(topic.strip()) > 1:
            unique_topics.append(topic.strip())

    # Limit to 5 most relevant topics
    return unique_topics[:5]


def process_needs_action_folder():
    """Process all emails in the needs_action folder and create Plan.md files."""
    needs_action_dir = Path("needs_action")
    print(f"Processing emails in {needs_action_dir}")

    # Get all JSON email files in the needs_action folder
    email_files = list(needs_action_dir.glob("*.json"))
    print(f"Found {len(email_files)} email files to process")

    for email_file in email_files:
        print(f"Processing {email_file.name}")

        try:
            # Extract content from the email
            email_content = extract_email_content(str(email_file))

            # Create Plan.md content with research
            plan_content = create_plan_for_email_with_research(email_content)

            # Create Plan.md file in the same directory as the email
            plan_file_path = email_file.parent / f"{email_file.stem}_Plan.md"

            # Write the plan to file
            with open(plan_file_path, 'w', encoding='utf-8', errors='replace') as plan_file:
                plan_file.write(plan_content)

            print(f"Created plan file: {plan_file_path}")

        except Exception as e:
            print(f"Error processing {email_file.name}: {e}")
            continue

    print("Finished processing all emails in needs_action folder")


if __name__ == "__main__":
    process_needs_action_folder()