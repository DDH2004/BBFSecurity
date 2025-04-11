from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import List, Dict, Any, Optional
from bson import ObjectId

from app.core.config import settings

client = None
db = None

async def connect_to_mongodb():
    """Create database connection."""
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
async def close_mongodb_connection():
    """Close database connection."""
    global client
    if client is not None:
        client.close()

async def get_collection(collection_name: str):
    """Get a collection by name."""
    return db[collection_name]

# Helper function to convert ObjectId to string
def serialize_doc(doc):
    if doc.get("_id") and isinstance(doc["_id"], ObjectId):
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc

# Dataset functions
async def fetch_datasets(query=None, limit=100):
    """Fetch datasets based on query parameters."""
    collection = await get_collection("datasets")
    query = query or {}
    cursor = collection.find(query).limit(limit)
    datasets = await cursor.to_list(length=limit)
    return [serialize_doc(doc) for doc in datasets]

async def get_dataset_by_id(dataset_id: str):
    """Get a dataset by its ID."""
    collection = await get_collection("datasets")
    try:
        obj_id = ObjectId(dataset_id)
        dataset = await collection.find_one({"_id": obj_id})
        if dataset:
            return serialize_doc(dataset)
        return None
    except Exception:
        # Handle invalid ObjectId format
        return None

# Agent result functions
async def store_agent_result(agent_id: str, result: dict):
    """Store results from an agent simulation."""
    collection = await get_collection("agent_results")
    document = {
        "agent_id": agent_id,
        "timestamp": datetime.utcnow(),
        **result
    }
    result = await collection.insert_one(document)
    return str(result.inserted_id)

async def get_agent_results(agent_id: Optional[str] = None, limit: int = 100):
    """Get results of agent simulations."""
    collection = await get_collection("agent_results")
    query = {"agent_id": agent_id} if agent_id else {}
    cursor = collection.find(query).sort("timestamp", -1).limit(limit)
    results = await cursor.to_list(length=limit)
    return [serialize_doc(doc) for doc in results]