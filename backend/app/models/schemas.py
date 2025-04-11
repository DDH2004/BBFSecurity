from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class QueryRequest(BaseModel):
    query: str
    document_ids: Optional[List[str]] = []

class QueryResponse(BaseModel):
    answer: str
    processed: bool = True

class DocumentResponse(BaseModel):
    id: str
    name: str
    upload_date: datetime
    size: Optional[int] = None
    mime_type: Optional[str] = None

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse] = []

class ErrorResponse(BaseModel):
    detail: str