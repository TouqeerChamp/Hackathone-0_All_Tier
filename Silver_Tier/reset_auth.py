#!/usr/bin/env python3
"""
Helper script to clean authentication token and prepare for new scopes
"""
import os

def reset_auth_token():
    """Remove the existing token file to force re-authentication with new scopes"""
    token_file = 'token.pickle'

    if os.path.exists(token_file):
        os.remove(token_file)
        print(f"Removed {token_file}. Please run your application again to re-authenticate with the new scopes.")
    else:
        print(f"{token_file} does not exist. You may run your application directly to authenticate.")

if __name__ == "__main__":
    reset_auth_token()