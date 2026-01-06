"""
Vercel Serverless Function Entry Point
This file is required for Vercel to properly deploy Python Flask apps
"""
from web_dashboard import app

# Vercel expects the app to be exported
# This file makes web_dashboard.py accessible as a serverless function
__all__ = ['app']
