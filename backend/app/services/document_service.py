import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..config import settings
from .midnight_service import get_midnight_client
from ..models.schemas import DocumentResponse

async def process_document(
    content: bytes, 
    filename: str, 
    mime_type: str, 
    user_id: str
) -> DocumentResponse:
    """
    Process an uploaded document through privacy layer and store securely
    """
    try:
        # Get Midnight client
        midnight = get_midnight_client()
        
        # Process document through Midnight (simulated for hackathon)
        processed_document = await midnight.process_user_document(
            document=content,
            user_id=user_id,
            document_type=mime_type
        )
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Ensure user directory exists
        user_dir = os.path.join(settings.UPLOAD_DIR, user_id)
        os.makedirs(user_dir, exist_ok=True)
        
        # Save document
        doc_path = os.path.join(user_dir, f"{document_id}.bin")
        with open(doc_path, "wb") as f:
            f.write(processed_document)
        
        # Save metadata
        metadata = {
            "id": document_id,
            "original_name": filename,
            "mime_type": mime_type,
            "size": len(content),
            "upload_date": datetime.now().isoformat()
        }
        
        meta_path = os.path.join(user_dir, f"{document_id}.meta.json")
        with open(meta_path, "w") as f:
            json.dump(metadata, f)
        
        return DocumentResponse(
            id=document_id,
            name=filename,
            upload_date=datetime.now(),
            size=len(content),
            mime_type=mime_type
        )
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        raise Exception("Failed to process document")

async def get_user_documents(user_id: str) -> List[DocumentResponse]:
    """
    Retrieve list of user's documents
    """
    try:
        user_dir = os.path.join(settings.UPLOAD_DIR, user_id)
        
        # Create directory if it doesn't exist
        os.makedirs(user_dir, exist_ok=True)
        
        documents = []
        
        # List files in user directory
        for filename in os.listdir(user_dir):
            if filename.endswith(".meta.json"):
                meta_path = os.path.join(user_dir, filename)
                with open(meta_path, "r") as f:
                    metadata = json.load(f)
                
                documents.append(DocumentResponse(
                    id=metadata["id"],
                    name=metadata["original_name"],
                    upload_date=datetime.fromisoformat(metadata["upload_date"]),
                    size=metadata.get("size"),
                    mime_type=metadata.get("mime_type")
                ))
        
        return documents
    except Exception as e:
        print(f"Error getting user documents: {str(e)}")
        raise Exception("Failed to retrieve documents")