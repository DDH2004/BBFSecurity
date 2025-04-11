from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any

from app.services.auth0_service import verify_jwt
from app.services.mongodb_service import fetch_datasets, get_dataset_by_id
from app.models.schemas import Dataset, DatasetQuery

router = APIRouter(prefix="/data", tags=["data"])

@router.get("/datasets", response_model=List[Dataset])
async def get_datasets(
    query: Optional[str] = Query(None, description="Filter query"),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(verify_jwt)
):
    """
    Retrieve datasets based on query parameters
    """
    query_dict = {}
    if query:
        # Parse query string into MongoDB query
        # This is a simple implementation; you might want more sophisticated query parsing
        query_dict = {"name": {"$regex": query, "$options": "i"}}
    
    try:
        datasets = await fetch_datasets(query_dict, limit)
        return datasets
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch datasets: {str(e)}"
        )

@router.get("/datasets/{dataset_id}", response_model=Dataset)
async def get_dataset(
    dataset_id: str,
    current_user: dict = Depends(verify_jwt)
):
    """
    Get a specific dataset by ID
    """
    dataset = await get_dataset_by_id(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset {dataset_id} not found"
        )
    return dataset