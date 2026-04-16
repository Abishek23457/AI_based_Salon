"""
AI Voice Service for Exotel Integration
Handles conversations with GPT-4 for voice calls
"""
import os
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from llm_chain import execute_chat, stream_chat, _get_gemini_llm  # Gemini instead of Groq
from database import SessionLocal
import models

# In-memory conversation cache (use Redis in production)
conversation_cache: Dict[str, list] = {}
booking_context: Dict[str, dict] = {}

# Salon configuration with 50+ slots
SALON_CONFIG = {
    "total_slots_per_day": 50,
    "slot_duration_minutes": 30,
    "opening_time": "10:00",
    "closing_time": "20:00",
    "services": {
        "haircut": {"duration": 30, "price": 500, "stylists": ["Priya", "Rahul", "Anita"]},
        "hair_coloring": {"duration": 90, "price": 2000, "stylists": ["Priya", "Anita"]},
        "facial": {"duration": 60, "price": 1500, "stylists": ["Rahul", "Sonia"]},
        "manicure": {"duration": 45, "price": 800, "stylists": ["Anita", "Sonia"]},
        "pedicure": {"duration": 45, "price": 800, "stylists": ["Anita", "Sonia"]},
        "massage": {"duration": 60, "price": 1800, "stylists": ["Rahul"]},
        "bridal_package": {"duration": 180, "price": 8000, "stylists": ["Priya"]},
    }
}


def get_system_prompt() -> str:
    """Enhanced system prompt with booking slot checking."""
    return """You are an AI voice assistant for BookSmart AI Salon handling phone bookings.

YOUR CAPABILITIES:
- Check available slots (50 slots per day)
- Check stylist availability for specific services
- Collect all required booking info: service, date, time, customer name, phone
- Confirm bookings before finalizing

BOOKING RULES:
1. Always check slot availability before confirming
2. Match service to available stylists (some services need specific stylists)
3. Collect all required info: service, date, time, name, phone number
4. Ask ONE question at a time - never ask multiple questions together
5. Confirm all details before finalizing booking
6. Keep responses under 20 words for voice clarity

CONVERSATION FLOW:
1. Greet caller
2. Identify requested service
3. Ask preferred date
4. Check available slots for that date
5. Offer 2-3 time options (e.g., "10 AM, 2 PM, or 4 PM")
6. Check if preferred stylist is available (optional)
7. Collect customer name
8. Collect phone number
9. Confirm all booking details
10. Provide booking confirmation with reference number

SAMPLE RESPONSES:
- "We have 45 slots open tomorrow. What time works? 10 AM, 2 PM, or 4 PM?"
- "Priya is available at 2 PM for haircut. May I have your name?"
- "Let me confirm: Haircut with Priya tomorrow at 2 PM. Your name is John, phone 9876543210. Correct?"
- "Perfect! Booking confirmed. Reference: BK123456. See you tomorrow!"

IMPORTANT: Never say "I don't know" - check the system or ask clarifying questions."""


def get_conversation_history(call_sid: str) -> list:
    """Get conversation history from cache."""
    return conversation_cache.get(call_sid, [])


def save_conversation_history(call_sid: str, history: list):
    """Save conversation history to cache."""
    conversation_cache[call_sid] = history
    # Limit cache size (simple eviction)
    if len(conversation_cache) > 1000:
        oldest_key = next(iter(conversation_cache))
        del conversation_cache[oldest_key]


def clear_conversation(call_sid: str):
    """Clear conversation history."""
    if call_sid in conversation_cache:
        del conversation_cache[call_sid]


# ─── Booking Context Management ─────────────────────────────────────────────

def get_booking_context(call_sid: str) -> dict:
    """Get or create booking context for this call."""
    if call_sid not in booking_context:
        booking_context[call_sid] = {
            "stage": "initial",
            "service": None,
            "date": None,
            "time": None,
            "stylist": None,
            "customer_name": None,
            "phone": None,
            "slots_available": None,
            "available_stylists": [],
            "booking_reference": None
        }
    return booking_context[call_sid]


def update_booking_context(call_sid: str, **kwargs):
    """Update booking context with new information."""
    context = get_booking_context(call_sid)
    context.update(kwargs)
    booking_context[call_sid] = context


def clear_booking_context(call_sid: str):
    """Clear booking context when call ends."""
    if call_sid in booking_context:
        del booking_context[call_sid]
    if call_sid in conversation_cache:
        del conversation_cache[call_sid]


# ─── Slot and Availability Checking ───────────────────────────────────────────

def check_slot_availability(date: str) -> dict:
    """Check available slots for a given date (50 slots total)."""
    import random
    booked_slots = random.randint(5, 35)  # Random bookings for demo
    total_slots = SALON_CONFIG["total_slots_per_day"]
    available = total_slots - booked_slots
    
    # Generate available time slots
    opening = datetime.strptime(SALON_CONFIG["opening_time"], "%H:%M")
    closing = datetime.strptime(SALON_CONFIG["closing_time"], "%H:%M")
    
    available_times = []
    current = opening
    while current < closing and len(available_times) < available:
        time_str = current.strftime("%I:%M %p")
        available_times.append(time_str)
        current += timedelta(minutes=SALON_CONFIG["slot_duration_minutes"])
    
    return {
        "total_slots": total_slots,
        "booked_slots": booked_slots,
        "available_slots": available,
        "available_times": available_times[:10],
        "is_available": available > 0
    }


def get_service_info(service_name: str) -> Optional[dict]:
    """Get service details and available stylists."""
    service_key = service_name.lower().replace(" ", "_").replace("&", "and")
    
    if service_key in SALON_CONFIG["services"]:
        return SALON_CONFIG["services"][service_key]
    
    # Try partial matches
    for key, info in SALON_CONFIG["services"].items():
        if key.replace("_", "") in service_key or service_key in key:
            return info
    
    return None


def check_stylist_availability(stylist: str, date: str, time: str) -> bool:
    """Check if specific stylist is available at given time."""
    import random
    return random.random() > 0.15  # 85% availability for demo


# ─── Input Parsing ─────────────────────────────────────────────────────────

def parse_date_from_input(user_input: str) -> Optional[str]:
    """Extract date from user input."""
    user_lower = user_input.lower()
    today = datetime.now()
    
    if "today" in user_lower:
        return today.strftime("%Y-%m-%d")
    elif "tomorrow" in user_lower:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "day after" in user_lower:
        return (today + timedelta(days=2)).strftime("%Y-%m-%d")
    
    # Parse day names
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for i, day in enumerate(days):
        if day in user_lower:
            target_day = i
            current_day = today.weekday()
            days_ahead = (target_day - current_day) % 7
            if days_ahead == 0:
                days_ahead = 7
            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    
    return None


def parse_time_from_input(user_input: str) -> Optional[str]:
    """Extract time from user input."""
    user_lower = user_input.lower()
    
    # Time patterns
    patterns = [
        (r'(\d+):(\d+)\s*(am|pm)', lambda m: f"{m.group(1)}:{m.group(2)} {m.group(3).upper()}"),
        (r'(\d+)\s*(am|pm)', lambda m: f"{m.group(1)}:00 {m.group(2).upper()}"),
    ]
    
    for pattern, formatter in patterns:
        match = re.search(pattern, user_lower)
        if match:
            return formatter(match)
    
    # Keywords
    if "morning" in user_lower:
        return "10:00 AM"
    elif "afternoon" in user_lower:
        return "02:00 PM"
    elif "evening" in user_lower:
        return "05:00 PM"
    
    return None


# ─── Booking State Processing ──────────────────────────────────────────────

def process_booking_input(call_sid: str, user_input: str, context: dict) -> dict:
    """Process user input and update booking context."""
    user_lower = user_input.lower()
    
    # Detect service
    if not context["service"]:
        for service_name in SALON_CONFIG["services"].keys():
            service_variations = [
                service_name.replace("_", " "),
                service_name.replace("_", ""),
                service_name.replace("_", " and ")
            ]
            for variation in service_variations:
                if variation.lower() in user_lower:
                    context["service"] = service_name.replace("_", " ").title()
                    service_info = get_service_info(service_name)
                    if service_info:
                        context["available_stylists"] = service_info["stylists"]
                    context["stage"] = "service_selected"
                    return context
    
    # Detect date
    if context["service"] and not context["date"]:
        parsed_date = parse_date_from_input(user_input)
        if parsed_date:
            context["date"] = parsed_date
            context["stage"] = "date_selected"
            slots = check_slot_availability(parsed_date)
            context["slots_available"] = slots["available_slots"]
            return context
    
    # Detect time
    if context["date"] and not context["time"]:
        parsed_time = parse_time_from_input(user_input)
        if parsed_time:
            context["time"] = parsed_time
            context["stage"] = "time_selected"
            return context
    
    # Detect stylist preference
    if context["time"] and context["available_stylists"]:
        for stylist in context["available_stylists"]:
            if stylist.lower() in user_lower:
                context["stylist"] = stylist
                context["stage"] = "stylist_selected"
                return context
    
    # Detect name
    if context["time"] and not context["customer_name"]:
        patterns = [r'my name is (\w+)', r'name is (\w+)', r'i am (\w+)', r'^(\w+)$']
        for pattern in patterns:
            match = re.search(pattern, user_lower)
            if match:
                context["customer_name"] = match.group(1).title()
                context["stage"] = "info_collected"
                return context
    
    # Detect phone
    if context["customer_name"] and not context["phone"]:
        phone_match = re.search(r'(\d{10})', user_input.replace(" ", "").replace("-", ""))
        if phone_match:
            context["phone"] = phone_match.group(1)
            context["stage"] = "info_collected"
            return context
    
    # Detect confirmation
    if context["stage"] == "info_collected":
        if any(word in user_lower for word in ["yes", "correct", "confirm", "sure", "ok", "okay"]):
            context["stage"] = "confirmed"
            context["booking_reference"] = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
            return context
    
    return context


def generate_booking_prompt(context: dict, user_input: str) -> str:
    """Generate context-aware prompt based on booking stage."""
    stage = context["stage"]
    
    if stage == "initial" and context["service"]:
        return f"Service: {context['service']}. Ask for preferred date."
    
    elif stage == "service_selected":
        slots = check_slot_availability(context.get("date", "tomorrow"))
        times = ", ".join(slots["available_times"][:3])
        return f"{slots['available_slots']} slots open. Suggest: {times}"
    
    elif stage == "date_selected":
        slots = check_slot_availability(context["date"])
        times = ", ".join(slots["available_times"][:3])
        return f"Date set. {slots['available_slots']} slots. Offer: {times}"
    
    elif stage == "time_selected":
        return f"Time {context['time']} confirmed. Collect customer name."
    
    elif stage == "stylist_selected":
        available = check_stylist_availability(context["stylist"], context["date"], context["time"])
        if available:
            return f"{context['stylist']} available. Collect customer name."
        else:
            others = ", ".join(context["available_stylists"][:2])
            return f"{context['stylist']} busy. Suggest: {others}"
    
    elif stage == "info_collected":
        return "Confirm all booking details and ask for final confirmation."
    
    elif stage == "confirmed":
        return "Booking confirmed. Provide reference number and offer more help."
    
    return "Continue conversation."


# ─── Main Voice Processing ─────────────────────────────────────────────────

def process_voice_input(call_sid: str, user_input: str, customer_context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Enhanced voice processing with booking management.
    """
    try:
        # Get or create booking context
        context = get_booking_context(call_sid)
        
        # Process user input and update context
        context = process_booking_input(call_sid, user_input, context)
        
        # Get conversation history
        history = get_conversation_history(call_sid)
        
        # Build enhanced prompt with booking context
        if not history:
            history = [{"role": "system", "content": get_system_prompt()}]
        
        # Add booking context to prompt
        booking_prompt = generate_booking_prompt(context, user_input)
        history.append({"role": "system", "content": booking_prompt})
        
        # Add user input
        history.append({"role": "user", "content": user_input})
        
        # Get AI response using Gemini
        try:
            db = SessionLocal()
            try:
                ai_message = execute_chat(db, 1, user_input) # salon_id=1 as default
            finally:
                db.close()
        except Exception as e:
            print(f"[Gemini Voice] Error: {e}")
            ai_message = generate_fallback_response(user_input, context)
        
        # Clean response
        ai_message = clean_response(ai_message)
        
        # Add to history
        history.append({"role": "assistant", "content": ai_message})
        save_conversation_history(call_sid, history)
        
        # Determine action
        action = determine_action(ai_message, user_input, context)
        
        return {
            "message": ai_message,
            "action": action,
            "call_sid": call_sid,
            "should_continue": action != "hangup",
            "booking_context": context
        }
        
    except Exception as e:
        print(f"[AI Voice] Error: {e}")
        return {
            "message": "I'm sorry, could you repeat that?",
            "action": "retry",
            "call_sid": call_sid,
            "should_continue": True,
            "booking_context": get_booking_context(call_sid)
        }


def clean_response(text: str) -> str:
    """Clean AI response for voice output."""
    # Remove markdown
    text = text.replace("**", "").replace("*", "")
    text = text.replace("`", "")
    text = text.replace("#", "")
    
    # Remove bullet points and numbers
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith("- ") or line.startswith("* "):
            line = line[2:]
        # Remove numbered lists
        if line and line[0].isdigit() and "." in line[:3]:
            line = line.split(".", 1)[1].strip()
        if line:
            cleaned_lines.append(line)
    
    return " ".join(cleaned_lines)


def determine_action(ai_message: str, user_input: str, context: dict = None) -> str:
    """Determine next action based on conversation and booking context."""
    user_lower = user_input.lower()
    ai_lower = ai_message.lower()
    
    # Check for hangup signals
    if any(phrase in ai_lower for phrase in ["goodbye", "thank you for calling", "have a great day", "bye bye"]):
        return "hangup"
    
    # Check for transfer request
    if any(phrase in user_lower for phrase in ["speak to human", "talk to manager", "representative", "real person", "someone else"]):
        return "transfer"
    
    # Check booking stage from context
    if context:
        stage = context.get("stage", "initial")
        if stage == "confirmed":
            return "booking_confirmed"
        elif stage == "info_collected" and context.get("service") and context.get("time"):
            return "booking_in_progress"
    
    # Check for booking intent
    if any(phrase in user_lower for phrase in ["book", "appointment", "schedule", "slot", "reserve"]):
        return "booking"
    
    # Check for cancellation
    if any(phrase in user_lower for phrase in ["cancel", "delete", "remove", "don't want"]):
        return "cancellation"
    
    # Check for inquiry
    if any(phrase in user_lower for phrase in ["price", "cost", "how much", "available", "timing", "hours", "open"]):
        return "inquiry"
    
    return "continue"


def generate_fallback_response(user_input: str, context: dict = None) -> str:
    """Generate context-aware fallback response with slot checking."""
    user_lower = user_input.lower()
    
    # Context-aware responses based on booking stage
    if context:
        stage = context.get("stage", "initial")
        service = context.get("service")
        date = context.get("date")
        time = context.get("time")
        stylist = context.get("stylist")
        name = context.get("customer_name")
        
        if stage == "service_selected":
            slots = check_slot_availability(context.get("date", "tomorrow"))
            times = ", ".join(slots["available_times"][:3])
            return f"We have {slots['available_slots']} slots open. Available times: {times}. Which works for you?"
        
        elif stage == "date_selected":
            return "What time would you prefer? We have morning, afternoon, and evening slots available."
        
        elif stage == "time_selected":
            return f"Great! May I have your name for the booking?"
        
        elif stage == "stylist_selected":
            return f"{stylist} is available at {time}. May I have your name?"
        
        elif stage == "info_collected":
            ref = context.get('booking_reference', 'BK' + datetime.now().strftime('%H%M%S'))
            return f"Let me confirm: {service} on {date} at {time}. Name: {name}. Reference: {ref}. Correct?"
        
        elif stage == "confirmed":
            ref = context.get('booking_reference', 'BK123456')
            return f"Perfect! Your booking is confirmed. Reference: {ref}. See you then!"
    
    # Default fallbacks
    if "book" in user_lower or "appointment" in user_lower:
        return "I'd be happy to help you book. What service would you like? We offer haircuts, coloring, facials, manicures, pedicures, and massages."
    elif "price" in user_lower or "cost" in user_lower:
        return "Haircuts start at 500 rupees, coloring at 2000, facials at 1500. What service interests you?"
    elif "slot" in user_lower or "available" in user_lower:
        return "We have 50 slots per day with many still open. What date would you prefer?"
    elif "hour" in user_lower or "open" in user_lower:
        return "We're open Monday to Saturday 10 AM to 8 PM, Sunday 11 AM to 6 PM."
    elif "stylist" in user_lower or "who" in user_lower:
        return "Our stylists are Priya, Rahul, Anita, and Sonia. Each specializes in different services."
    elif "hello" in user_lower or "hi" in user_lower:
        return "Hello! Welcome to BookSmart AI Salon. I'm your virtual receptionist. How can I help you today?"
    else:
        return "I understand. Are you looking to book an appointment, or do you have questions about our services?"


def detect_intent(user_input: str) -> str:
    """Simple intent detection for routing."""
    user_lower = user_input.lower()
    
    intents = {
        "booking": ["book", "appointment", "schedule", "reserve", "slot"],
        "inquiry": ["price", "cost", "how much", "available", "services", "what do you offer"],
        "hours": ["hour", "open", "close", "timing", "when"],
        "location": ["where", "location", "address", "find you"],
        "cancel": ["cancel", "delete", "remove"],
        "reschedule": ["change", "reschedule", "move", "different time"],
        "human": ["human", "person", "manager", "representative", "talk to someone"]
    }
    
    for intent, keywords in intents.items():
        if any(keyword in user_lower for keyword in keywords):
            return intent
    
    return "general"
