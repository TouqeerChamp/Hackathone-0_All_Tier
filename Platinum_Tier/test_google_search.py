"""
Test script to verify Google Search API credentials are working correctly.
This tests the direct API connection using the provided credentials.
"""

import os
from dotenv import load_dotenv
import requests

# Load environment variables from explicit path
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Get credentials from .env (with fallback to direct values)
API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyDi0Oi_1h0uEermw3lLhTY2GZGF--EDuN4')
CX_ID = os.getenv('GOOGLE_CSE_ID', 'b73821318aa53412b')

print("=" * 60)
print("Google Search API Connection Test")
print("=" * 60)
print(f"API Key: {API_KEY[:10]}...{API_KEY[-5:]}")
print(f"CX ID: {CX_ID}")
print("=" * 60)

# Test the Google Custom Search API
query = "Latest AI automation trends 2026"
url = "https://www.googleapis.com/customsearch/v1"
params = {
    'key': API_KEY,
    'cx': CX_ID,
    'q': query,
    'num': 5
}

print(f"\nSearching for: '{query}'")
print("-" * 60)

try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    
    if 'items' in data:
        print(f"\n✓ SUCCESS! Found {len(data['items'])} results:\n")
        for i, item in enumerate(data['items'], 1):
            print(f"{i}. {item.get('title', 'No title')}")
            print(f"   URL: {item.get('link', 'No link')}")
            print(f"   Snippet: {item.get('snippet', 'No snippet')[:150]}...")
            print()
    else:
        print("\n✗ No results found. Check your API credentials.")
        print(f"Response: {data}")
        
except requests.exceptions.HTTPError as e:
    print(f"\n✗ HTTP Error: {e}")
    print(f"Response: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"\n✗ Request Error: {e}")
except Exception as e:
    print(f"\n✗ Error: {e}")

print("=" * 60)
print("Test completed!")
