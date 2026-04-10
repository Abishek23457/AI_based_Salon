"""
Intelligent AI Receptionist that understands the salon business and user needs
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
from datetime import datetime
import re
from llm_chain import execute_chat, _get_gemini_llm
from database import SessionLocal
import models

router = APIRouter(prefix="/ai-receptionist", tags=["AI Receptionist"])

class ChatMessage(BaseModel):
    message: str
    salon_id: Optional[str] = "1"
    customer_name: Optional[str] = "Customer"
    customer_phone: Optional[str] = None

class IntelligentAIReceptionist:
    def __init__(self):
        self.salon_info = {
            "name": "BookSmart AI Salon",
            "services": {
                "hair": ["Haircut", "Hair Coloring", "Hair Styling", "Hair Treatment", "Blow Dry", "Keratin Treatment"],
                "beauty": ["Facial", "Makeup", "Waxing", "Threading", "Manicure", "Pedicure"],
                "spa": ["Massage", "Body Treatment", "Aromatherapy", "Hot Stone Massage"],
                "bridal": ["Bridal Makeup", "Bridal Hair", "Pre-bridal Package"]
            },
            "prices": {
                "haircut": 500,
                "hair coloring": 1500,
                "facial": 800,
                "massage": 1200,
                "bridal package": 15000
            },
            "duration": {
                "haircut": "30 minutes",
                "hair coloring": "2 hours",
                "facial": "1 hour",
                "massage": "1.5 hours",
                "bridal package": "4-6 hours"
            },
            "staff": {
                "hair_stylists": ["Sarah", "John", "Emma"],
                "beauty_experts": ["Lisa", "Maria", "Sophia"],
                "massage_therapists": ["David", "Robert", "James"]
            },
            "hours": {
                "monday": "9:00 AM - 7:00 PM",
                "tuesday": "9:00 AM - 7:00 PM", 
                "wednesday": "9:00 AM - 7:00 PM",
                "thursday": "9:00 AM - 7:00 PM",
                "friday": "9:00 AM - 7:00 PM",
                "saturday": "9:00 AM - 7:00 PM",
                "sunday": "10:00 AM - 5:00 PM"
            },
            "contact": {
                "phone": "+91-9876543210",
                "email": "info@booksmart.ai",
                "address": "123 Main Street, City Center",
                "website": "www.booksmart.ai"
            }
        }
        
        # User intent patterns
        self.intent_patterns = {
            "booking": ["book", "appointment", "schedule", "reserve", "time slot"],
            "pricing": ["price", "cost", "rate", "how much", "charge", "fee"],
            "services": ["service", "treatment", "what do you offer", "available"],
            "hours": ["hours", "time", "open", "close", "when"],
            "contact": ["contact", "phone", "email", "address", "location"],
            "staff": ["staff", "stylist", "expert", "therapist", "who"],
            "bridal": ["bridal", "wedding", "marriage", "bride"],
            "emergency": ["urgent", "emergency", "asap", "today", "now"],
            "complaint": ["complaint", "issue", "problem", "unhappy", "bad"],
            "compliment": ["great", "excellent", "amazing", "love", "happy"]
        }

    def analyze_user_intent(self, message: str) -> str:
        """Analyze user message to determine intent using Gemini"""
        try:
            llm = _get_gemini_llm()
            prompt = f"""
            Analyze the following message from a salon customer and identify their primary intent.
            Return ONLY the intent keyword from this list: booking, pricing, services, hours, contact, staff, bridal, emergency, complaint, compliment, general.
            
            Message: {message}
            Intent:"""
            response = llm.invoke(prompt)
            intent = getattr(response, "content", "general").strip().lower()
            
            # Simple validation
            valid_intents = ["booking", "pricing", "services", "hours", "contact", "staff", "bridal", "emergency", "complaint", "compliment", "general"]
            for valid in valid_intents:
                if valid in intent:
                    return valid
            return "general"
        except Exception as e:
            print(f"[Gemini Intent] Error: {e}")
            return "general"

    def extract_service_info(self, message: str) -> Optional[str]:
        """Extract specific service mentioned by user"""
        message_lower = message.lower()
        
        for category, services in self.salon_info["services"].items():
            for service in services:
                if service.lower() in message_lower:
                    return service
        
        # Check for general categories
        if any(word in message_lower for word in ["hair", "haircut"]):
            return "hair"
        elif any(word in message_lower for word in ["beauty", "facial", "makeup"]):
            return "beauty"
        elif any(word in message_lower for word in ["massage", "spa"]):
            return "spa"
        elif any(word in message_lower for word in ["bridal", "wedding"]):
            return "bridal"
        
        return None

    def generate_intelligent_response(self, message: str, customer_name: str = "Customer") -> Dict:
        """Generate intelligent response using Gemini with business context"""
        try:
            db = SessionLocal()
            try:
                # Use the centralized Gemini logic from llm_chain
                response_text = execute_chat(db, 1, message) # default salon_id=1
                
                # Still analyze intent for metadata
                intent = self.analyze_user_intent(message)
                service = self.extract_service_info(message)
                
                return {
                    "response": response_text,
                    "intent": intent,
                    "service_detected": service,
                    "customer_name": customer_name,
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                }
            finally:
                db.close()
        except Exception as e:
            print(f"[Gemini Intelligent] Error: {e}")
            return {
                "response": "I'm your AI assistant for BookSmart AI Salon! I can help you with appointments, pricing, services, and more. How can I help today?",
                "status": "fallback",
                "error": str(e)
            }

# Initialize AI Receptionist
ai_receptionist = IntelligentAIReceptionist()

@router.post("/chat")
async def intelligent_chat(chat: ChatMessage):
    """Intelligent AI chat that understands user needs"""
    try:
        response = ai_receptionist.generate_intelligent_response(
            chat.message, 
            chat.customer_name or "Customer"
        )
        return response
    except Exception as e:
        return {
            "response": "I apologize, but I'm having trouble processing your request. Please call us at +91-9876543210 for immediate assistance.",
            "status": "error",
            "error": str(e)
        }

@router.get("/status")
async def ai_status():
    """Get AI receptionist status"""
    return {
        "status": "intelligent",
        "capabilities": [
            "Intent recognition",
            "Service detection", 
            "Personalized responses",
            "Business context awareness",
            "User sentiment analysis"
        ],
        "services_offered": list(ai_receptionist.salon_info["services"].keys()),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/services")
async def get_services():
    """Get all available services with details"""
    return {
        "salon_info": ai_receptionist.salon_info,
        "timestamp": datetime.now().isoformat()
    }
