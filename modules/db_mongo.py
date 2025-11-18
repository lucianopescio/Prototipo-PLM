"""
Simple MongoDB helper using pymongo and `database.config` for URI.
Provides a get_db() convenience function.
"""
from typing import Optional
from pymongo import MongoClient
from database.config import DB_URI, DB_NAME

_client: Optional[MongoClient] = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(DB_URI)
    return _client


def get_db():
    client = get_client()
    return client[DB_NAME]


def get_collection(name: str):
    db = get_db()
    return db[name]
