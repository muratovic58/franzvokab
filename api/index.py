import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Add the parent directory to sys.path so we can import from the parent directory
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    logger.info(f"Python path: {sys.path}")
    
    # Import the Flask app from app.py
    from app import app
    
    # Log environment variables (excluding sensitive ones)
    env_vars = {k: v for k, v in os.environ.items() if 'SECRET' not in k and 'PASSWORD' not in k and 'KEY' not in k}
    logger.info(f"Environment variables: {env_vars}")
    
    # Log app configuration
    logger.info(f"App config: {app.config}")
    
    # This is the handler for Vercel serverless functions
    # The variable 'app' is imported by Vercel
    
except Exception as e:
    logger.error(f"Error initializing app: {str(e)}")
    raise

# For local development
if __name__ == "__main__":
    app.run(debug=True)
