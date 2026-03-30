import re

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

    print(f"Content: {content}")

    # Check for Urdu script (Unicode ranges for Arabic/Persian characters used in Urdu)
    has_urdu_script = any('\u0600' <= char <= '\u06FF' for char in content)
    print(f"Has Urdu script: {has_urdu_script}")

    # Check for Roman Urdu patterns (common Urdu words written in Latin script)
    roman_urdu_patterns = ['kaise', 'kya', 'hai', 'ke', 'ka', 'ki', 'na', 'kar', 'ho', 'ay']
    has_roman_urdu = any(pattern in content.lower() for pattern in roman_urdu_patterns)
    print(f"Has Roman Urdu: {has_roman_urdu}")

    # Check for simple indicators with word boundaries
    for indicator in simple_indicators:
        pattern = r'\b' + re.escape(indicator) + r'\b'
        match = re.search(pattern, content.lower())
        if match:
            print(f"Found simple indicator: '{indicator}' matching at position {match.start()}-{match.end()}")
            return "simple"
        else:
            print(f"No match for simple indicator: '{indicator}'")

    print("--- Checked all simple indicators ---")

    # Check for complex indicators with word boundaries
    for indicator in complex_indicators:
        pattern = r'\b' + re.escape(indicator) + r'\b'
        match = re.search(pattern, content.lower())
        if match:
            print(f"Found complex indicator: '{indicator}' matching at position {match.start()}-{match.end()}")
            return "complex"
        else:
            print(f"No match for complex indicator: '{indicator}'")

    print("--- Checked all complex indicators ---")

    # If contains Urdu script or Roman Urdu patterns, categorize as complex (likely needs human understanding)
    if has_urdu_script or has_roman_urdu:
        print("Has Urdu script or Roman Urdu patterns - returning complex")
        return "complex"

    # If content is very short, consider it simple
    if len(content) < 20:
        print("Content is short - returning simple")
        return "simple"

    # Default to complex if uncertain
    print("Defaulting to complex")
    return "complex"

# Test with the actual content from the file
with open('done/urdu_task.txt', 'r', encoding='utf-8') as f:
    content = f.read().strip()

print(f"Testing with content: {repr(content)}")
result = categorize_task(content)
print(f"Final result: {result}")