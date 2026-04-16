"""
Simple Chat Receptionist that works
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
from datetime import datetime

router = APIRouter(tags=["Chat"])

class ChatMessage(BaseModel):
    message: str
    salon_id: Optional[str] = "1"
    customer_name: Optional[str] = "Customer"

# Simple chat responses
CHAT_RESPONSES = {
    "hello": "Hello! Welcome to BookSmart AI. How can I help you today?",
    "hi": "Hi there! Welcome to our salon. What can I do for you?",
    "booking": "I can help you book an appointment! What service would you like?",
    "appointment": "I'd be happy to schedule an appointment for you. What day works best?",
    "services": "We offer hair styling, beauty treatments, massage therapy, and more. What interests you?",
    "price": "Our prices vary by service. Which service would you like pricing for?",
    "hours": "We're open Monday-Saturday 9AM-7PM. Sunday 10AM-5PM.",
    "contact": "You can reach us at +91-9876543210 or email us at info@booksmart.ai",
    "location": "We're located at 123 Main Street, City Center. Come visit us!",
    "default": "Thank you for your message! Our staff will assist you shortly. You can also call us for immediate assistance."
}

@router.post("/receptionist")
async def chat_receptionist(chat: ChatMessage):
    """Simple chat receptionist that always works"""
    try:
        message_lower = chat.message.lower()
        
        # Find matching response
        response = CHAT_RESPONSES.get("default")
        for key in CHAT_RESPONSES:
            if key in message_lower:
                response = CHAT_RESPONSES[key]
                break
        
        return {
            "user_message": chat.message,
            "ai_response": response,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        return {
            "user_message": chat.message,
            "ai_response": "I'm here to help! Please call us at +91-9876543210 for immediate assistance.",
            "timestamp": datetime.now().isoformat(),
            "status": "fallback",
            "error": str(e)
        }

@router.get("/status")
async def chat_status():
    """Get chat system status"""
    return {
        "status": "working",
        "message": "Chat receptionist is operational",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chat-receptionist"}
