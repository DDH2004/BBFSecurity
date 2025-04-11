from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_auth0 import Auth0User
from ..models.schemas import QueryRequest, QueryResponse
from ..services.ai_service import process_query
from .auth import auth0

router = APIRouter(prefix="/queries", tags=["queries"])

@router.post("/", response_model=QueryResponse)
async def submit_query(
    query_data: QueryRequest,
    user: Auth0User = Depends(auth0.get_user)
):
    """Process a user query securely and return AI-generated response"""
    try:
        response = await process_query(query_data.query, query_data.document_ids, user.id)
        return {"answer": response, "processed": True}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )