"""
AI Receptionist that understands user texting flow and natural conversation patterns
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
from datetime import datetime
import re

router = APIRouter(prefix="/texting-ai", tags=["Texting AI"])

class ChatMessage(BaseModel):
    message: str
    salon_id: Optional[str] = "1"
    customer_name: Optional[str] = "Customer"
    customer_phone: Optional[str] = None
    conversation_context: Optional[List[Dict]] = None

class TextingAIReceptionist:
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
        
        # Texting patterns and user flow understanding
        self.texting_patterns = {
            # Initial contact patterns
            "greeting": ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"],
            "introduction": ["my name is", "i'm", "this is", "it's"],
            
            # Information seeking patterns
            "price_inquiry": ["how much", "price", "cost", "rate", "charge", "fee", "how much does"],
            "availability": ["available", "free", "when can", "what time", "slot", "opening"],
            "service_inquiry": ["what services", "do you offer", "what do you do", "services"],
            "location_inquiry": ["where", "address", "location", "directions"],
            
            # Booking patterns
            "booking_intent": ["book", "appointment", "schedule", "reserve", "want to", "need"],
            "time_preference": ["today", "tomorrow", "this week", "next week", "asap", "urgent"],
            "specific_time": ["9am", "10am", "11am", "2pm", "3pm", "4pm", "5pm", "6pm"],
            
            # Confirmation patterns
            "confirmation": ["yes", "yeah", "sure", "ok", "confirm", "sounds good", "perfect"],
            "cancellation": ["cancel", "no", "can't", "not available", "change"],
            "reschedule": ["reschedule", "change time", "different time", "move"],
            
            # Casual texting patterns
            "casual": ["thanks", "thank you", "awesome", "great", "cool", "ok", "k"],
            "questions": ["?", "??", "how", "what", "when", "where", "why"],
            
            # Emergency/urgent patterns
            "urgent": ["urgent", "emergency", "asap", "right now", "immediately", "today please"],
            
            # Service specific patterns
            "hair_related": ["haircut", "hair", "cut", "style", "color", "highlight", "trim"],
            "beauty_related": ["facial", "makeup", "wax", "thread", "manicure", "pedicure"],
            "spa_related": ["massage", "spa", "relax", "treatment", "therapy"],
            "bridal_related": ["bridal", "wedding", "marriage", "bride", "marriage"]
        }
        
        # Conversation state tracking
        self.conversation_states = {
            "initial": "greeting",
            "information": "inquiry",
            "booking": "booking_process",
            "confirmation": "confirmed",
            "followup": "follow_up"
        }
        
        # Natural response templates
        self.response_templates = {
            "greeting": [
                "Hi there! Welcome to {salon_name}! How can I help you today? {emoji}",
                "Hello! Thanks for reaching out to {salon_name}! What can I do for you? {emoji}",
                "Hey! Welcome to {salon_name}! I'm here to help with your beauty needs. {emoji}"
            ],
            "price_response": [
                "Our {service} costs {price} and takes {duration}. Would you like to book an appointment? {emoji}",
                "For {service}, we charge {price} ({duration}). When would you like to come in? {emoji}",
                "{service} is {price} and takes about {duration}. Should I book you in? {emoji}"
            ],
            "booking_confirmation": [
                "Perfect! I've got you down for {service} on {date} at {time}. See you then! {emoji}",
                "Awesome! Your {service} appointment is set for {date} at {time}. Can't wait to see you! {emoji}",
                "Great choice! You're all set for {service} on {date} at {time}. See you soon! {emoji}"
            ],
            "casual_acknowledgment": [
                "Sounds good! {emoji}",
                "Perfect! {emoji}",
                "Great! {emoji}",
                "Awesome! {emoji}",
                "Cool! {emoji}"
            ]
        }

    def analyze_texting_pattern(self, message: str, conversation_history: List[Dict] = None) -> Dict:
        """Analyze texting patterns and user flow"""
        message_lower = message.lower().strip()
        
        # Detect conversation stage
        if not conversation_history or len(conversation_history) == 0:
            conversation_stage = "initial"
        elif len(conversation_history) <= 3:
            conversation_stage = "information"
        elif any("book" in msg.get("content", "").lower() for msg in conversation_history[-3:]):
            conversation_stage = "booking"
        else:
            conversation_stage = "followup"
        
        # Detect user intent and patterns
        detected_patterns = []
        intent = "general"
        
        for pattern_type, keywords in self.texting_patterns.items():
            for keyword in keywords:
                if keyword in message_lower:
                    detected_patterns.append(pattern_type)
                    if pattern_type in ["booking_intent", "price_inquiry", "service_inquiry"]:
                        intent = pattern_type
                    break
        
        # Extract specific information
        service_mentioned = self.extract_service_from_text(message)
        time_mentioned = self.extract_time_from_text(message)
        urgency = "urgent" in detected_patterns
        
        return {
            "conversation_stage": conversation_stage,
            "intent": intent,
            "detected_patterns": detected_patterns,
            "service_mentioned": service_mentioned,
            "time_mentioned": time_mentioned,
            "urgency": urgency,
            "message_type": self.classify_message_type(message_lower, detected_patterns)
        }

    def extract_service_from_text(self, message: str) -> Optional[str]:
        """Extract service mentioned in text"""
        message_lower = message.lower()
        
        for category, services in self.salon_info["services"].items():
            for service in services:
                if service.lower() in message_lower:
                    return service
        
        # Check for general categories
        if any(word in message_lower for word in ["haircut", "cut", "trim"]):
            return "haircut"
        elif any(word in message_lower for word in ["facial", "face"]):
            return "facial"
        elif any(word in message_lower for word in ["massage", "spa"]):
            return "massage"
        elif any(word in message_lower for word in ["bridal", "wedding"]):
            return "bridal package"
        
        return None

    def extract_time_from_text(self, message: str) -> Optional[str]:
        """Extract time preferences from text"""
        message_lower = message.lower()
        
        time_patterns = {
            "today": ["today", "right now", "asap"],
            "tomorrow": ["tomorrow", "tmrw"],
            "this_week": ["this week", "sometime this week"],
            "morning": ["morning", "am", "9am", "10am", "11am"],
            "afternoon": ["afternoon", "pm", "12pm", "1pm", "2pm", "3pm", "4pm", "5pm"],
            "evening": ["evening", "6pm", "7pm"]
        }
        
        for time_type, keywords in time_patterns.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return time_type
        
        return None

    def classify_message_type(self, message: str, patterns: List[str]) -> str:
        """Classify the type of message"""
        if "greeting" in patterns:
            return "greeting"
        elif "booking_intent" in patterns:
            return "booking_request"
        elif "price_inquiry" in patterns:
            return "price_question"
        elif "confirmation" in patterns:
            return "confirmation"
        elif "questions" in patterns:
            return "question"
        elif "casual" in patterns:
            return "casual"
        else:
            return "statement"

    def generate_texting_response(self, message: str, customer_name: str = "Customer", conversation_history: List[Dict] = None) -> Dict:
        """Generate natural texting response"""
        
        # Analyze the message
        analysis = self.analyze_texting_pattern(message, conversation_history)
        
        # Personalize greeting
        if customer_name != "Customer":
            greeting = f"Hi {customer_name}! "
        else:
            greeting = "Hi there! "
        
        # Generate contextual response
        response = ""
        next_action = None
        
        if analysis["message_type"] == "greeting":
            if analysis["conversation_stage"] == "initial":
                response = f"{greeting}Welcome to {self.salon_info['name']}! I'm here to help with appointments, services, pricing, or any questions you have. What are you looking for today? "
            else:
                response = f"{greeting}Good to hear from you again! How can I help you today? "
        
        elif analysis["message_type"] == "booking_request":
            service = analysis["service_mentioned"]
            time = analysis["time_mentioned"]
            
            if service:
                price = self.salon_info["prices"].get(service.lower(), "varies")
                duration = self.salon_info["duration"].get(service.lower(), "varies")
                response = f"Great choice! I can book you for {service}. It takes {duration} and costs {price}. "
                
                if time:
                    response += f"I see you want to come {time}. Let me check availability... "
                    next_action = "check_availability"
                else:
                    response += "What day and time works best for you? "
                    next_action = "ask_time"
            else:
                response = f"Sure! What service would you like to book? We offer hair services, beauty treatments, spa services, and bridal packages. "
                next_action = "ask_service"
        
        elif analysis["message_type"] == "price_question":
            service = analysis["service_mentioned"]
            if service:
                price = self.salon_info["prices"].get(service.lower(), "varies")
                duration = self.salon_info["duration"].get(service.lower(), "varies")
                response = f"Our {service} is {price} and takes {duration}. Would you like to book an appointment? "
                next_action = "offer_booking"
            else:
                response = "Our prices vary by service. Haircuts start at 500, facials at 800, massages at 1200, and bridal packages at 15000. Which service are you interested in? "
                next_action = "ask_service"
        
        elif analysis["message_type"] == "question":
            if "hours" in message.lower() or "time" in message.lower():
                response = f"We're open Mon-Sat 9AM-7PM and Sunday 10AM-5PM. When would you like to visit? "
            elif "location" in message.lower() or "address" in message.lower():
                response = f"We're at {self.salon_info['contact']['address']}. Easy to find! Would you like directions? "
            elif "services" in message.lower():
                response = "We offer: Hair services (cut, color, styling), Beauty treatments (facial, makeup, waxing), Spa services (massage, therapy), and Bridal packages. What interests you? "
            else:
                response = "Good question! Can you tell me more about what you'd like to know? I'm here to help with appointments, services, pricing, and more. "
        
        elif analysis["message_type"] == "confirmation":
            response = "Perfect! I've got that down. Is there anything else I can help you with? "
        
        elif analysis["message_type"] == "casual":
            casual_responses = ["Sounds good! ", "Great! ", "Perfect! ", "Awesome! ", "Cool! "]
            response = casual_responses[hash(message) % len(casual_responses)]
            if analysis["conversation_stage"] == "booking":
                response += "Your appointment is all set. See you soon! "
            else:
                response += "How else can I help you today? "
        
        else:
            # General response
            response = f"Thanks for your message! I'm here to help with your salon needs. You can ask me about booking appointments, services, prices, or anything else. What would you like to know? "
        
        # Add emojis for natural texting feel
        if not response.endswith(("?", "!", ".")):
            response += " "
        
        # Add appropriate emojis
        if analysis["message_type"] == "greeting":
            response += " "
        elif analysis["message_type"] == "booking_request":
            response += ""
        elif analysis["message_type"] == "confirmation":
            response += ""
        else:
            response += ""
        
        return {
            "response": response,
            "analysis": analysis,
            "next_action": next_action,
            "customer_name": customer_name,
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "conversation_stage": analysis["conversation_stage"]
        }

# Initialize Texting AI
texting_ai = TextingAIReceptionist()

@router.post("/chat")
async def texting_chat(chat: ChatMessage):
    """AI that understands texting flow and natural conversation"""
    try:
        response = texting_ai.generate_texting_response(
            chat.message, 
            chat.customer_name or "Customer",
            chat.conversation_context or []
        )
        return response
    except Exception as e:
        return {
            "response": "Hey! I'm here to help with your salon needs. You can ask me about booking, services, prices, or anything else! ",
            "status": "fallback",
            "error": str(e)
        }

@router.post("/analyze")
async def analyze_texting_pattern(message: str, conversation_history: List[Dict] = None):
    """Analyze texting patterns for debugging"""
    try:
        analysis = texting_ai.analyze_texting_pattern(message, conversation_history or [])
        return {
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/status")
async def texting_ai_status():
    """Get texting AI status"""
    return {
        "status": "texting_ai_ready",
        "capabilities": [
            "Natural texting conversation",
            "User flow understanding",
            "Conversation context awareness",
            "Service and time extraction",
            "Pattern recognition",
            "Casual texting responses"
        ],
        "supported_patterns": list(texting_ai.texting_patterns.keys()),
        "timestamp": datetime.now().isoformat()
    }
