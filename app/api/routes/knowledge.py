from fastapi import APIRouter, Depends, HTTPException
from app.schemas.knowledge import DocumentUpload, DocumentQuery
from app.services.midnight_service import MidnightService
from app.services.gemini_service import GeminiService
from app.core.security import get_current_user

router = APIRouter()

@router.post("/upload")
async def upload_document(document: DocumentUpload, user=Depends(get_current_user)):
    try:
        # Use MidnightService to handle document upload securely
        result = await MidnightService.upload_document(document, user)
        return {"message": "Document uploaded successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/query")
async def query_document(query: DocumentQuery, user=Depends(get_current_user)):
    try:
        # Use GeminiService to process the query on the uploaded documents
        response = await GeminiService.query_documents(query, user)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))