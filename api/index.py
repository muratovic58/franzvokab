import sys
import os

# Add the parent directory to sys.path so we can import from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app from app.py
from app import app

# This is the handler for Vercel serverless functions

# For local development
if __name__ == "__main__":
    app.run(debug=True)
