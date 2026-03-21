import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
url = os.getenv("DATABASE_URL")
print(f"--- Attempting to connect to: {url} ---")

try:
    engine = create_engine(url)
    with engine.connect() as conn:
        print("✅ SUCCESS: Database connection established!")
except Exception as e:
    print(f"❌ FAILED: {e}")