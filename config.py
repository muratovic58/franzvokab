import os
from dotenv import load_dotenv
import warnings
from urllib.parse import quote_plus
from sqlalchemy.engine.url import make_url

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
    
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise ValueError('DATABASE_URL environment variable is not set!')
    try:
        url = make_url(db_url)
        SQLALCHEMY_DATABASE_URI = db_url
        DB_USERNAME = url.username
        DB_PASSWORD = url.password
        DB_HOST = url.host
        DB_PORT = url.port
        DB_NAME = url.database
    except Exception as e:
        raise ValueError(f'Error parsing DATABASE_URL: {e}')
    
    # Debug output
    print(f"SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
