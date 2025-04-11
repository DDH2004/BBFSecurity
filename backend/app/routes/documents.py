from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi_auth0 import Auth0User
from typing import List
import os
from datetime import datetime
from ..config import settings
from ..services.document_service import process_document, get_user_documents
from ..models.schemas import DocumentResponse, DocumentListResponse
from .auth import auth0

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    document: UploadFile = File(...),
    user: Auth0User = Depends(auth0.get_user)
):
    """Upload and process a document securely"""
    # Read file content
    content = await document.read()
    
    try:
        result = await process_document(content, document.filename, document.content_type, user.id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )

@router.get("/", response_model=DocumentListResponse)
async def list_documents(user: Auth0User = Depends(auth0.get_user)):
    """List all documents for the current user"""
    try:
        documents = await get_user_documents(user.id)
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving documents: {str(e)}"
        )
