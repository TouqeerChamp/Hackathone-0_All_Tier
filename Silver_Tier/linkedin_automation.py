"""
LinkedIn Automation - Draft Generator
=====================================
This script uses Google Search MCP to find trending AI automation topics
and generates LinkedIn post drafts promoting Mohammad Touqeer's services
as an Agentic AI Developer.

NOTE: This script only creates drafts. It does NOT post to LinkedIn.
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Enable UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

# Google Search API credentials
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyDi0Oi_1h0uEermw3lLhTY2GZGF--EDuN4')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID', 'b73821318aa53412b')


def search_google(query: str, num_results: int = 5) -> list:
    """
    Search Google using the Custom Search API.
    
    Args:
        query: Search query string
        num_results: Number of results to return (default: 5)
    
    Returns:
        List of search result items
    """
    import requests
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': GOOGLE_API_KEY,
        'cx': GOOGLE_CSE_ID,
        'q': query,
        'num': min(num_results, 10)  # API max is 10
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('items', [])
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print(f"⚠️  Warning: API quota exceeded. Using cached/trending topics.")
            return []
        print(f"Search error: {e}")
        return []
    except Exception as e:
        print(f"Search error: {e}")
        return []


def get_ai_automation_trends() -> list:
    """
    Find top AI automation trends for March 2026 using Google Search.
    
    Returns:
        List of trend topics with titles and snippets
    """
    print("🔍 Searching for AI automation trends for March 2026...")
    
    # Search for latest trends
    trends_query = "AI automation trends March 2026"
    results = search_google(trends_query, num_results=5)
    
    trends = []
    
    if results:
        # Extract unique trends from search results
        seen_topics = set()
        for result in results:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            
            # Extract key topics from titles and snippets
            for text in [title, snippet]:
                # Look for trend indicators
                if any(keyword in text.lower() for keyword in ['agentic', 'autonomous', 'workflow', 'automation', 'ai-powered']):
                    if text not in seen_topics and len(text) > 20:
                        trends.append({
                            'title': title,
                            'snippet': snippet,
                            'url': result.get('link', '')
                        })
                        seen_topics.add(text)
                        
                        if len(trends) >= 3:
                            break
        
        if len(trends) < 3:
            # Fallback: search for more specific trends
            fallback_queries = [
                "agentic AI 2026",
                "AI workflow automation 2026",
                "autonomous AI agents business"
            ]
            for query in fallback_queries:
                if len(trends) >= 3:
                    break
                additional = search_google(query, num_results=3)
                for result in additional:
                    title = result.get('title', '')
                    if title not in seen_topics:
                        trends.append({
                            'title': title,
                            'snippet': result.get('snippet', ''),
                            'url': result.get('link', '')
                        })
                        seen_topics.add(title)
    
    # Fallback trends if API quota exceeded or no results
    if not trends:
        print("   Using known trending topics for March 2026...")
        trends = [
            {
                'title': 'Agentic AI: Autonomous Systems for Business',
                'snippet': 'Agentic AI systems can now plan and execute multi-step business tasks autonomously, transforming how enterprises scale operations in 2026.',
                'url': 'https://example.com/agentic-ai-trends'
            },
            {
                'title': 'AI-Powered Workflow Automation at Scale',
                'snippet': 'Businesses are deploying AI automation that goes beyond simple tasks to handle complex, multi-department workflows with minimal human intervention.',
                'url': 'https://example.com/workflow-automation'
            },
            {
                'title': 'Hyper-Personalized Customer Experiences with AI',
                'snippet': 'AI-driven personalization engines are creating unique customer journeys, boosting engagement and conversion rates across industries.',
                'url': 'https://example.com/ai-personalization'
            }
        ]
    
    return trends[:3]


def generate_linkedin_post(trends: list) -> str:
    """
    Generate a LinkedIn post draft based on AI automation trends.
    
    Args:
        trends: List of trend dictionaries with title, snippet, url
    
    Returns:
        Formatted LinkedIn post as a string
    """
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Extract key themes from trends
    themes = []
    for trend in trends:
        title = trend.get('title', '')
        # Extract key phrases
        if 'agentic' in title.lower() or 'autonomous' in title.lower():
            themes.append("🤖 Agentic AI & Autonomous Systems")
        elif 'workflow' in title.lower() or 'automation' in title.lower():
            themes.append("⚡ AI-Powered Workflow Automation")
        elif 'personal' in title.lower() or 'customer' in title.lower():
            themes.append("🎯 Hyper-Personalized AI Experiences")
        else:
            themes.append(f"💡 {title.split(':')[0] if ':' in title else title[:50]}")
    
    # Remove duplicates while preserving order
    unique_themes = list(dict.fromkeys(themes))
    
    post = f"""
================================================================================
LINKEDIN POST DRAFT
Generated: {current_date}
Topic: AI Automation Trends & Mohammad Touqeer's Services
================================================================================

🚀 THE FUTURE OF AI AUTOMATION IS HERE! 🚀

As we move through March 2026, the AI landscape is evolving faster than ever.
Here are the TOP 3 trends shaping the industry:

"""
    
    for i, theme in enumerate(unique_themes[:3], 1):
        post += f"{i}. {theme}\n"
    
    post += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💼 IS YOUR BUSINESS READY FOR THIS AI REVOLUTION?

Hi, I'm Mohammad Touqeer 👋

As an Agentic AI Developer, I specialize in building intelligent automation 
solutions that don't just follow rules—they THINK, PLAN, and EXECUTE.

✅ WHAT I OFFER:
   • Custom Agentic AI Systems
   • End-to-End Workflow Automation
   • AI-Powered Business Process Optimization
   • Intelligent Chatbots & Virtual Assistants
   • Data-Driven Decision Making Solutions

✅ WHY WORK WITH ME:
   • Cutting-edge AI implementations
   • Tailored solutions for YOUR business needs
   • Focus on ROI and measurable outcomes
   • Continuous support and optimization

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 REAL RESULTS:
   → Reduce operational costs by up to 60%
   → Automate 80%+ of repetitive tasks
   → Scale your operations without scaling headcount
   → Make data-driven decisions in real-time

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 LET'S TRANSFORM YOUR BUSINESS TOGETHER!

Ready to leverage these AI trends for YOUR competitive advantage?

📩 DM me or email: [Your Email Here]
🔗 Portfolio: [Your Portfolio/Website]
📍 Location: [Your Location / Remote Available]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#AIAutomation #AgenticAI #ArtificialIntelligence #BusinessAutomation 
#MachineLearning #DigitalTransformation #AI2026 #TechInnovation 
#WorkflowAutomation #FutureOfWork #AIDeveloper #AutomationExpert

================================================================================
END OF DRAFT
================================================================================

SOURCES CONSULTED:
"""
    
    for i, trend in enumerate(trends, 1):
        post += f"\n{i}. {trend.get('title', 'N/A')}\n   {trend.get('url', 'N/A')}\n"
    
    post += f"""

---
NOTE: This is a DRAFT only. Review and customize before posting.
Replace bracketed placeholders [Your Email Here], [Your Portfolio/Website], 
and [Your Location] with actual contact information.
"""
    
    return post


def save_draft(post: str, output_dir: str = "linkedin_drafts") -> str:
    """
    Save the LinkedIn post draft to a text file.
    
    Args:
        post: The LinkedIn post content
        output_dir: Directory to save the draft
    
    Returns:
        Path to the saved file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"linkedin_draft_{timestamp}.txt"
    filepath = os.path.join(output_dir, filename)
    
    # Save the draft
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(post)
    
    return filepath


def main():
    """Main function to orchestrate the LinkedIn draft generation."""
    print("=" * 70)
    print("LINKEDIN AUTOMATION - DRAFT GENERATOR")
    print("=" * 70)
    print()
    
    # Step 1: Get AI automation trends
    trends = get_ai_automation_trends()
    
    if trends:
        print(f"   ✓ Found {len(trends)} trending topics")
        for i, trend in enumerate(trends, 1):
            print(f"   {i}. {trend.get('title', 'N/A')[:60]}...")
    else:
        print("   ⚠️  No trends found, using fallback topics")
    
    print()
    
    # Step 2: Generate LinkedIn post
    print("📝 Generating LinkedIn post draft...")
    post = generate_linkedin_post(trends)
    
    # Step 3: Save the draft
    print("💾 Saving draft to file...")
    filepath = save_draft(post)
    
    print()
    print("=" * 70)
    print("✅ DRAFT CREATED SUCCESSFULLY!")
    print("=" * 70)
    print(f"📁 Saved to: {os.path.abspath(filepath)}")
    print()
    print("📋 PREVIEW:")
    print("-" * 70)
    # Show first 500 characters as preview
    print(post[:500] + "...\n[See file for full content]")
    print("-" * 70)
    print()
    print("⚠️  REMINDER: This is a DRAFT ONLY. Review before posting!")
    print("=" * 70)
    
    return filepath


if __name__ == "__main__":
    main()
