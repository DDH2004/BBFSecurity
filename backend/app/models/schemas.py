# filepath: /workspaces/BBFSecurity/backend/app/models/schemas.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class UserInfo(BaseModel):
    id: str
    email: Optional[str] = None
    is_active: bool = True

# Agent schemas
class Agent(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

class AgentSimulationRequest(BaseModel):
    agent_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    datasets: Optional[List[str]] = None

class AgentSimulationResponse(BaseModel):
    agent_id: str
    result_id: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    raw_response: Optional[str] = None

# Dataset schemas
class DatasetQuery(BaseModel):
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 100

class Dataset(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    sample_data: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)