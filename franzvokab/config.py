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
    
    # If using Postgres on Railway, make sure to replace 'postgres://' with 'postgresql://'
    if raw_db_url and raw_db_url.startswith('postgres://'):
        raw_db_url = raw_db_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = raw_db_url
    
    # Debug output
    print(f"SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
