"""Direct test without dotenv"""
import requests

API_KEY = 'AIzaSyDi0Oi_1h0uEermw3lLhTY2GZGF--EDuN4'
CX_ID = 'b73821318aa53412b'

print(f"Testing with API Key: {API_KEY[:10]}...{API_KEY[-5:]}")
print(f"CX ID: {CX_ID}")

query = "Latest AI automation trends 2026"
url = "https://www.googleapis.com/customsearch/v1"
params = {'key': API_KEY, 'cx': CX_ID, 'q': query, 'num': 5}

print(f"\nSearching for: '{query}'\n")

response = requests.get(url, params=params, timeout=30)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    if 'items' in data:
        print(f"\n✓ SUCCESS! Found {len(data['items'])} results:\n")
        for i, item in enumerate(data['items'], 1):
            print(f"{i}. {item.get('title', 'No title')}")
            print(f"   URL: {item.get('link', 'No link')}")
            print()
    else:
        print(f"\nNo results: {data}")
else:
    print(f"\n✗ Error: {response.text}")
