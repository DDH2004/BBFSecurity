from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    user_id: str
    query: str

class ChatResponse(BaseModel):
    response: str
    confidence: Optional[float] = None

class ChatHistory(BaseModel):
    user_id: str
    messages: List[ChatRequest]