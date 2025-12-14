from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

# Try DATABASE_URL first (for cloud deployment like Render)
database_url = os.getenv("db_connection_string")

if not database_url:
    # Fall back to individual environment variables for local development
    host = os.getenv("host")
    database = os.getenv("database")
    user = os.getenv("user")
    password = os.getenv("password")
    port = os.getenv("port")

    # Validate that all required env vars are loaded
    if not all([host, database, user, password, port]):
        raise ValueError("Missing required environment variables in .env file: host, database, user, password, port")

    # Encode the password to handle special characters like @
    encoded_password = quote_plus(password)
    database_url = f'postgresql+psycopg2://{user}:{encoded_password}@{host}:{port}/{database}'

### connection using SQLAlchemy (if needed)
def make_sqlalchemy_db_connection():
    """Create a SQLAlchemy engine for the PostgreSQL database."""
    engine = None
    try:
        engine = create_engine(database_url)
        print("SQLAlchemy engine created successfully")
    except Exception as e:
        print(f"Error: {e}")
    return engine