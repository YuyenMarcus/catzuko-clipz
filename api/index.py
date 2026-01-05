"""
Vercel serverless function entry point for Clipfarm Dashboard
"""
from web_dashboard import app

# Vercel expects the app to be named 'app'
# This is a handler for Vercel's serverless functions
def handler(request):
    return app(request.environ, lambda status, headers: None)

# For Vercel Python runtime
app = app

