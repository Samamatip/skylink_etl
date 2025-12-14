from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

host = os.getenv("host")
database = os.getenv("database")
user = os.getenv("user")
password = os.getenv("password")
port = os.getenv("port")
full_db_connection_string = os.getenv("db_connection_string")

# Encode the password to handle special characters like @
encoded_password = quote_plus(password)

db_connection_string = full_db_connection_string or f'postgresql+psycopg2://{user}:{encoded_password}@{host}:{port}/{database}'

# Validate that all required env vars are loaded
if not all([host, database, user, password, port]):
    raise ValueError("Missing required environment variables in .env file: host, database, user, password, port")

### connection using SQLAlchemy (if needed)
def make_sqlalchemy_db_connection():
    """Create a SQLAlchemy engine for the PostgreSQL database."""
    engine = None
    try:
        engine = create_engine(db_connection_string)
        print("SQLAlchemy engine created successfully")
    except Exception as e:
        print(f"Error: {e}")
    return engine