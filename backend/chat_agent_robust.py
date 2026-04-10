"""
Robust Chat Agent with Gemini LLM and Exotel fallback handling
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import models
from database import get_db
import asyncio

# Import Gemini LLM
try:
    from google import genai
    from config import settings
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    GEMINI_AVAILABLE = True
except Exception as e:
    print(f"Warning: Gemini not available: {e}")
    GEMINI_AVAILABLE = False

# Import Exotel client
try:
    from exotel_client import exotel_client
    EXOTEL_AVAILABLE = True
except Exception as e:
    print(f"Warning: Exotel not available: {e}")
    EXOTEL_AVAILABLE = False

router = APIRouter(prefix="/chat-agent", tags=["Chat Agent"])

# Local storage for chat history and customer data
CHAT_STORAGE_FILE = "chat_storage.json"
CUSTOMER_DATA_FILE = "customer_data.json"

def load_chat_history(salon_id: str) -> List[Dict]:
    """Load chat history from local storage"""
    try:
        if os.path.exists(CHAT_STORAGE_FILE):
            with open(CHAT_STORAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get(salon_id, [])
        return []
    except Exception as e:
        print(f"Error loading chat history: {e}")
        return []

def save_chat_history(salon_id: str, message: Dict):
    """Save chat message to local storage"""
    try:
        data = {}
        if os.path.exists(CHAT_STORAGE_FILE):
            with open(CHAT_STORAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        if salon_id not in data:
            data[salon_id] = []
        
        message['timestamp'] = datetime.now().isoformat()
        data[salon_id].append(message)
        
        with open(CHAT_STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving chat history: {e}")

def load_customer_data() -> List[Dict]:
    """Load customer data from local storage"""
    try:
        if os.path.exists(CUSTOMER_DATA_FILE):
            with open(CUSTOMER_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading customer data: {e}")
        return []

def save_customer_data(data: List[Dict]):
    """Save customer data to local storage"""
    try:
        with open(CUSTOMER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving customer data: {e}")

async def get_gemini_response(message: str, salon_context: str = "") -> str:
    """Get response from Gemini LLM"""
    if not GEMINI_AVAILABLE:
        return f"AI Response: I understand you said '{message}'. (Gemini not available)"
    
    try:
        # Create context-aware prompt
        prompt = f"""
        You are a helpful AI assistant for a salon management system called BookSmart AI.
        
        Context: {salon_context}
        Customer message: {message}
        
        Provide a helpful, professional response. If the customer is asking about bookings, 
        services, or appointments, provide relevant information. Keep responses concise and friendly.
        """
        
        response = await asyncio.to_thread(gemini_model.generate_content, prompt)
        return response.text
    except Exception as e:
        print(f"Gemini error: {e}")
        return f"I apologize, but I'm having trouble processing your request right now. You said: {message}"

async def send_sms_notification(phone_number: str, message: str) -> bool:
    """Send SMS via Exotel with fallback"""
    if not EXOTEL_AVAILABLE:
        print(f"[SMS Fallback] Would send to {phone_number}: {message}")
        return True
    
    try:
        result = await exotel_client.send_sms(phone_number, message)
        return result is not None
    except Exception as e:
        print(f"SMS sending failed: {e}")
        return False

@router.post("/chat")
async def chat_with_ai(
    message: str,
    salon_id: str,
    customer_phone: Optional[str] = None,
    customer_name: Optional[str] = None,
    send_sms: bool = False
):
    """Chat with AI using Gemini LLM and optional SMS notification"""
    try:
        # Load chat history for context
        history = load_chat_history(salon_id)
        salon_context = f"Salon ID: {salon_id}, Recent chats: {len(history)} messages"
        
        # Get AI response from Gemini
        ai_response = await get_gemini_response(message, salon_context)
        
        # Save user message
        user_message = {
            "role": "user",
            "content": message,
            "customer_phone": customer_phone,
            "customer_name": customer_name,
            "timestamp": datetime.now().isoformat()
        }
        save_chat_history(salon_id, user_message)
        
        # Save AI response
        ai_message = {
            "role": "assistant", 
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        }
        save_chat_history(salon_id, ai_message)
        
        # Send SMS notification if requested
        sms_sent = False
        if send_sms and customer_phone:
            sms_message = f"BookSmart AI: {ai_response[:100]}..." if len(ai_response) > 100 else f"BookSmart AI: {ai_response}"
            sms_sent = await send_sms_notification(customer_phone, sms_message)
        
        return {
            "user_message": message,
            "ai_response": ai_response,
            "timestamp": datetime.now().isoformat(),
            "sms_sent": sms_sent,
            "gemini_available": GEMINI_AVAILABLE,
            "exotel_available": EXOTEL_AVAILABLE
        }
        
    except Exception as e:
        # Fallback response even if everything fails
        fallback_response = f"I understand you're asking about: {message}. I'm here to help with your salon needs."
        
        return {
            "user_message": message,
            "ai_response": fallback_response,
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "fallback_mode": True
        }

@router.get("/history/{salon_id}")
async def get_chat_history(salon_id: str):
    """Get chat history for a salon"""
    history = load_chat_history(salon_id)
    return {"history": history}

@router.get("/status")
async def get_system_status():
    """Get system status and availability"""
    return {
        "gemini_available": GEMINI_AVAILABLE,
        "exotel_available": EXOTEL_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/import-customers")
async def import_customers(file: UploadFile = File(...)):
    """Import customer data from Excel file"""
    try:
        # Check file extension
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only Excel files are supported")
        
        # Read file content
        content = await file.read()
        
        # Create temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Read Excel file
            df = pd.read_excel(temp_file_path)
            
            # Convert to list of dictionaries
            customers = df.to_dict('records')
            
            # Save to local storage
            save_customer_data(customers)
            
            return {
                "message": f"Successfully imported {len(customers)} customers",
                "count": len(customers),
                "customers": customers[:5]  # Return first 5 as preview
            }
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import error: {str(e)}")

@router.get("/export-customers")
async def export_customers():
    """Export customer data to Excel file"""
    try:
        # Load customer data
        customers = load_customer_data()
        
        if not customers:
            raise HTTPException(status_code=404, detail="No customer data to export")
        
        # Convert to DataFrame
        df = pd.DataFrame(customers)
        
        # Generate Excel file
        filename = f"customers_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = f"temp_{filename}"
        df.to_excel(filepath, index=False)
        
        # Read file and return as response
        with open(filepath, 'rb') as f:
            content = f.read()
        
        # Clean up temp file
        os.remove(filepath)
        
        from fastapi.responses import Response
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")

@router.get("/customers")
async def get_customers():
    """Get all customer data"""
    customers = load_customer_data()
    return {"customers": customers}

@router.post("/customer")
async def add_customer(customer_data: Dict[str, Any]):
    """Add a new customer"""
    try:
        customers = load_customer_data()
        customer_data['id'] = len(customers) + 1
        customer_data['created_at'] = datetime.now().isoformat()
        customers.append(customer_data)
        save_customer_data(customers)
        
        return {"message": "Customer added successfully", "customer": customer_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding customer: {str(e)}")

@router.delete("/customer/{customer_id}")
async def delete_customer(customer_id: int):
    """Delete a customer"""
    try:
        customers = load_customer_data()
        customers = [c for c in customers if c.get('id') != customer_id]
        save_customer_data(customers)
        
        return {"message": "Customer deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting customer: {str(e)}")
