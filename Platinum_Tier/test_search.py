#!/usr/bin/env python3
"""
Test script to verify Google Search MCP functionality
"""
import json
import subprocess
import sys
from pathlib import Path

def test_google_search():
    """Test the Google Search MCP service"""
    try:
        # Prepare input data
        input_data = {
            "query": "test search",
            "num_results": 3
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

        print("Return code:", result.returncode)
        print("Stdout:", result.stdout)
        print("Stderr:", result.stderr)

        if result.returncode != 0:
            print("Error calling MCP service")
        else:
            search_result = json.loads(result.stdout)
            print("Search result:", search_result)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_google_search()