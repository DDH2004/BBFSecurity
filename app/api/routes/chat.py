from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.gemini_service import get_ai_response
from app.core.security import get_current_user

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest, current_user: str = Depends(get_current_user)):
    response = await get_ai_response(request.query)
    return ChatResponse(response=response)