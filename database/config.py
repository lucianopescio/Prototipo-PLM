# database/config.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Read MongoDB URI and DB name from environment, with sensible defaults
DB_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", os.getenv("MONGO_DB", "tesis_db"))

# Logging
print(f"[DB CONFIG] Connecting to MongoDB at: {DB_URI.split('@')[0] if '@' in DB_URI else DB_URI[:50]}...")
print(f"[DB CONFIG] Using database: {DB_NAME}")