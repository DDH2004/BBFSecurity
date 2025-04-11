from pydantic import BaseModel
from typing import List, Optional

class DocumentUpload(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = None

class DocumentQuery(BaseModel):
    query: str
    document_id: str

class DocumentResponse(BaseModel):
    document_id: str
    title: str
    content: str
    tags: Optional[List[str]] = None
    relevance_score: float