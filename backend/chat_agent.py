"""
Chat Agent with local storage and Excel import/export functionality
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

# Try to import llm_chain, but handle if it doesn't exist
try:
    from llm_chain import execute_chat
except ImportError:
    print("Warning: llm_chain not found, using mock responses")
    def execute_chat(salon_id: str, message: str):
        return f"AI Response to: {message} (Mock mode - llm_chain not available)"

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

@router.post("/chat")
async def chat_with_history(
    message: str,
    salon_id: str,
    customer_phone: Optional[str] = None,
    customer_name: Optional[str] = None
):
    """Chat with AI and save conversation history"""
    try:
        # Get AI response
        ai_response = execute_chat(salon_id, message)
        
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
        
        return {
            "user_message": message,
            "ai_response": ai_response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.get("/history/{salon_id}")
async def get_chat_history(salon_id: str):
    """Get chat history for a salon"""
    history = load_chat_history(salon_id)
    return {"history": history}

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
