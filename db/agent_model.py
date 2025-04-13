# db/agent_model.py
import os
from datetime import datetime
from typing import Optional, Dict, Any

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

# ------------------------------------------------------------------
# Connection helper
# ------------------------------------------------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB   = os.getenv("MONGO_DB",   "aihacks")

_client = MongoClient(MONGO_URI)
_db     = _client[MONGO_DB]
_agents: Collection = _db["agents"]

# Ensure unique index on first run
_agents.create_index("agent_id", unique=True)


# ------------------------------------------------------------------
# CRUD helpers
# ------------------------------------------------------------------
def add_agent(agent_id: str,
              wallet_seed: str,
              contract_hex: str,
              public_key: Optional[str] = None,
              roles: Optional[list[str]] = None,
              active: bool = True) -> str:
    """
    Insert a new agent document. Returns inserted_id as str.
    """
    doc = {
        "agent_id": agent_id,
        "wallet_seed": wallet_seed,
        "contract_hex": contract_hex,
        "public_key": public_key,
        "roles": roles or ["read"],
        "active": active,
        "created_at": datetime.utcnow()
    }
    try:
        result = _agents.insert_one(doc)
        return str(result.inserted_id)
    except DuplicateKeyError:
        raise ValueError(f"Agent {agent_id} already exists")


def get_agent(agent_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a single agent record by agent_id.
    Returns None if not found or inactive.
    """
    return _agents.find_one({"agent_id": agent_id, "active": True})


def update_contract(agent_id: str, new_contract_hex: str) -> bool:
    """
    Change the contract an agent logs to.
    """
    res = _agents.update_one(
        {"agent_id": agent_id},
        {"$set": {"contract_hex": new_contract_hex}}
    )
    return res.modified_count == 1
