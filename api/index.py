"""
Vercel Serverless Function Entry Point
This file is required for Vercel to properly deploy Python Flask apps
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from web_dashboard import app

# Vercel expects the app to be exported
# This file makes web_dashboard.py accessible as a serverless function
__all__ = ['app']
