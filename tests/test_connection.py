import os
from dotenv import load_dotenv
import psycopg2
from config.config import DATABASE_CONFIG

def test_database_connection():
    """Test database connection"""
    try:
        # Print the actual configuration being used
        print(f"Attempting to connect to database with config: {DATABASE_CONFIG}")
        
        # Ensure port is an integer
        port = int(DATABASE_CONFIG["port"])
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=DATABASE_CONFIG["host"],
            port=port,
            database=DATABASE_CONFIG["database"],
            user=DATABASE_CONFIG["user"],
            password=DATABASE_CONFIG["password"]
        )
        print("✅ Database connection successful!")
        
        # Test if we can query the database
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL version: {version[0]}")
        
        # Test if we can access our database
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()
        print(f"✅ Connected to database: {db_name[0]}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure PostgreSQL is running (check Services)")
        print("2. Verify the database 'news_analyzer' exists")
        print("3. Check if the port 5432 is correct")
        print("4. Verify username and password in .env file")
        print("\nCurrent configuration:")
        print(f"Host: {DATABASE_CONFIG['host']}")
        print(f"Port: {DATABASE_CONFIG['port']}")
        print(f"Database: {DATABASE_CONFIG['database']}")
        print(f"User: {DATABASE_CONFIG['user']}")

def test_api_keys():
    """Test if API keys are set"""
    load_dotenv()
    news_api_key = os.getenv("NEWS_API_KEY")
    gnews_api_key = os.getenv("GNEWS_API_KEY")
    
    if news_api_key and news_api_key != "your_newsapi_key_here":
        print("✅ News API key is set")
    else:
        print("❌ News API key is not set or is using default value")
        print("   Get your API key from: https://newsapi.org/")
    
    if gnews_api_key and gnews_api_key != "your_gnews_key_here":
        print("✅ GNews API key is set")
    else:
        print("❌ GNews API key is not set or is using default value")
        print("   Get your API key from: https://gnews.io/")

if __name__ == "__main__":
    print("Running system tests...")
    print("\nTesting database connection:")
    test_database_connection()
    print("\nTesting API keys:")
    test_api_keys() 