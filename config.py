import os
from dotenv import load_dotenv
import warnings
from urllib.parse import quote_plus

# Suppress warnings about deprecated classifiers
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load environment variables with UTF-8 encoding
try:
    load_dotenv(encoding='utf-8')
except Exception as e:
    print(f"Warning: Error loading .env file: {str(e)}")
    # Try again with cp1252 encoding (Windows default)
    try:
        load_dotenv(encoding='cp1252')
    except Exception as e:
        print(f"Warning: Error loading .env file with cp1252: {str(e)}")

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev-key-for-development-only')
    
    # Get the database URL from environment
    raw_db_url = os.environ.get('DATABASE_URL', 'sqlite:///franzvokab.db')
    
    # Handle special characters in the password
    if '@' in raw_db_url:
        parts = raw_db_url.split('@')
        auth = parts[0]
        host = parts[1]
        
        # Split username:password
        if ':' in auth:
            user_pass = auth.split(':')[1]
            username = user_pass.split(':')[0]
            password = user_pass.split(':')[1]
            
            # URL encode the password
            encoded_password = quote_plus(password)
            
            # Reconstruct the URL with encoded password
            raw_db_url = f"postgresql://{username}:{encoded_password}@{host}"
    
    # If using Postgres on Railway, make sure to replace 'postgres://' with 'postgresql://'
    if raw_db_url and raw_db_url.startswith('postgres://'):
        raw_db_url = raw_db_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = raw_db_url
    
    # Debug output
    print(f"SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
