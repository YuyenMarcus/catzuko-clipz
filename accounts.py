"""
Helper to load accounts from JSON file
"""
import json
from pathlib import Path

def get_accounts():
    """Load accounts from accounts.json"""
    accounts_file = Path("accounts.json")
    if accounts_file.exists():
        with open(accounts_file, 'r') as f:
            return json.load(f)
    return {'tiktok': [], 'instagram': [], 'youtube': []}

