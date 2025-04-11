import httpx
import json
from typing import List, Optional
from ..config import settings
from .midnight_service import get_midnight_client

async def process_query(query: str, document_ids: Optional[List[str]] = None, user_id: str = None):
    """
    Process a user query through privacy layer and Gemini API
    """
    try:
        # Get Midnight client
        midnight = get_midnight_client()
        
        # Apply privacy rules to the query (simulated for hackathon)
        processed_query = await midnight.process_user_query(
            query=query,
            user_id=user_id,
            context={"document_ids": document_ids or []}
        )
        
        # Call Gemini API
        response = await call_gemini_api(processed_query)
        
        # Process response through Midnight again for privacy
        safe_response = await midnight.process_ai_response(
            response=response,
            user_id=user_id
        )
        
        return safe_response
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        raise Exception("Failed to process your query")

async def call_gemini_api(query: str):
    """
    Call the Google Gemini API with the processed query
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.GEMINI_API_URL,
                json={
                    "contents": [{
                        "parts": [{
                            "text": query
                        }]
                    }]
                },
                params={"key": settings.GEMINI_API_KEY},
                headers={"Content-Type": "application/json"}
            )
            
            # Handle errors
            if response.status_code != 200:
                print(f"Gemini API error: {response.text}")
                raise Exception(f"AI service error: {response.status_code}")
                
            result = response.json()
            
            # Extract text from Gemini response
            try:
                text_response = result["candidates"][0]["content"]["parts"][0]["text"]
                return text_response
            except (KeyError, IndexError) as e:
                print(f"Error parsing Gemini response: {str(e)}")
                raise Exception("Could not parse AI response")
    except httpx.RequestError as e:
        print(f"Request error: {str(e)}")
        raise Exception("Could not connect to AI service")