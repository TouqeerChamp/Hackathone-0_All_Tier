#!/usr/bin/env python3
"""
Google Custom Search MCP Service
"""
import os
import json
import sys
from typing import Dict, Any, Optional
import urllib.parse

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Google API libraries
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print(json.dumps({"error": "google-api-python-client not installed. Please install it with 'pip install google-api-python-client'"}), file=sys.stderr)
    sys.exit(1)


def get_google_api_credentials():
    """Get Google API credentials from environment variables or credentials file."""
    api_key = os.getenv('GOOGLE_API_KEY')
    cse_id = os.getenv('GOOGLE_CSE_ID')

    if not api_key or not cse_id:
        # Try to read from a config file
        config_path = os.path.join(os.path.dirname(__file__), 'google_config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    api_key = config.get('GOOGLE_API_KEY')
                    cse_id = config.get('GOOGLE_CSE_ID')
            except Exception as e:
                return None, None

    return api_key, cse_id


def google_search(query: str, num_results: int = 5) -> Dict[str, Any]:
    """
    Perform a Google search using the Custom Search API.

    Args:
        query: The search query
        num_results: Number of results to return (default 5)

    Returns:
        Dictionary containing search results
    """
    api_key, cse_id = get_google_api_credentials()

    if not api_key or not cse_id:
        return {
            "error": "Google API Key or Custom Search Engine ID not configured. Please set GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables."
        }

    try:
        service = build('customsearch', 'v1', developerKey=api_key)

        # Perform the search
        result = service.cse().list(
            q=query,
            cx=cse_id,
            num=min(num_results, 10)  # Google API limits to 10 results per request
        ).execute()

        # Extract relevant information from results
        search_items = result.get('items', [])
        results = []

        for item in search_items:
            result_item = {
                'title': item.get('title'),
                'link': item.get('link'),
                'snippet': item.get('snippet')
            }
            results.append(result_item)

        return {
            'query': query,
            'results': results,
            'total_results': len(results)
        }

    except HttpError as e:
        return {
            "error": f"HTTP error occurred: {e}"
        }
    except Exception as e:
        return {
            "error": f"An error occurred: {str(e)}"
        }


def main():
    """Main function to handle tool calls."""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command provided"}))
        return

    command = sys.argv[1]

    if command == "google_search":
        try:
            # Read input from stdin
            input_str = sys.stdin.read().strip()

            # If input is empty, read from command line arguments
            if not input_str and len(sys.argv) > 2:
                query = sys.argv[2]
                num_results = int(sys.argv[3]) if len(sys.argv) > 3 else 5
                input_data = {'query': query, 'num_results': num_results}
            else:
                input_data = json.loads(input_str)

            query = input_data.get('query')
            num_results = input_data.get('num_results', 5)

            result = google_search(query, num_results)
            print(json.dumps(result))
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Error parsing input JSON: {str(e)}"}))
        except Exception as e:
            print(json.dumps({"error": f"Error processing google_search: {str(e)}"}))
    else:
        print(json.dumps({"error": f"Unknown command: {command}"}))


if __name__ == "__main__":
    main()