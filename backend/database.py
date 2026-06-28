"""
database.py - MongoDB Atlas connection and CRUD helpers for Viettel Auto-Tuner
"""

import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Load .env file
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = "viettel_autotuner"
COLLECTION_NAME = "tuning_runs"

_client = None
_collection = None


def get_collection():
    """Lazy-initialize and return the MongoDB collection."""
    global _client, _collection
    if _collection is None:
        try:
            _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            # Ping to verify connection
            _client.admin.command("ping")
            db = _client[DB_NAME]
            _collection = db[COLLECTION_NAME]
            print(f"[MongoDB] Connected to Atlas -> {DB_NAME}.{COLLECTION_NAME}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"[MongoDB] Connection FAILED: {e}")
            _collection = None
    return _collection


def log_history(entry: dict):
    """Insert one tuning run record into MongoDB. Falls back silently on error."""
    try:
        col = get_collection()
        if col is None:
            return
        # Always store a clean ISO timestamp
        entry.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        # Remove any ObjectId before inserting (clean dict)
        entry.pop("_id", None)
        col.insert_one(entry)
    except Exception as e:
        print(f"[MongoDB] log_history error: {e}")


def get_history(limit: int = 100) -> list:
    """Return up to `limit` most recent records, oldest-id first."""
    try:
        col = get_collection()
        if col is None:
            return []
        return list(
            col.find({}, {"_id": 0})
               .sort("timestamp", DESCENDING)
               .limit(limit)
        )
    except Exception as e:
        print(f"[MongoDB] get_history error: {e}")
        return []


def clear_history() -> int:
    """Delete all records. Returns number of deleted documents."""
    try:
        col = get_collection()
        if col is None:
            return 0
        result = col.delete_many({})
        return result.deleted_count
    except Exception as e:
        print(f"[MongoDB] clear_history error: {e}")
        return 0


def get_stats() -> dict:
    """Return a quick summary of stored runs grouped by algorithm."""
    try:
        col = get_collection()
        if col is None:
            return {}
        pipeline = [
            {"$group": {
                "_id": "$algorithm",
                "count": {"$sum": 1},
                "best_itae": {"$min": "$metrics.pitch.itae"}
            }},
            {"$sort": {"count": DESCENDING}}
        ]
        rows = list(col.aggregate(pipeline))
        return {r["_id"]: {"count": r["count"], "best_itae": r.get("best_itae")} for r in rows}
    except Exception as e:
        print(f"[MongoDB] get_stats error: {e}")
        return {}
