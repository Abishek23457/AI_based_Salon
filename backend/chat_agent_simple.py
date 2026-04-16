"""
Simplified Chat Agent for testing
"""
import json
from datetime import datetime
from fastapi import APIRouter

router = APIRouter(prefix="/chat-agent", tags=["Chat Agent"])

@router.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Chat agent is working", "timestamp": datetime.now().isoformat()}

@router.get("/customers")
async def get_customers():
    """Get all customer data"""
    return {"customers": [], "message": "No customers yet"}

@router.post("/chat")
async def chat_endpoint(message: str, salon_id: str):
    """Simple chat endpoint"""
    return {
        "user_message": message,
        "ai_response": f"AI response to: {message}",
        "salon_id": salon_id,
        "timestamp": datetime.now().isoformat()
    }
