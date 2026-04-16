"""
WhatsApp API Router for BookSmart AI
API endpoints for WhatsApp messaging
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from whatsapp_client import whatsapp_client, send_whatsapp_booking_confirmation, send_whatsapp_reminder

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

class WhatsAppMessageRequest(BaseModel):
    to_number: str
    template_name: Optional[str] = None
    message: Optional[str] = None
    language_code: str = "en"

class BookingConfirmationRequest(BaseModel):
    to_number: str
    customer_name: str
    service: str
    date: str
    time: str
    booking_ref: str

class ReminderRequest(BaseModel):
    to_number: str
    customer_name: str
    service: str
    time: str

@router.post("/send-message")
async def send_message(request: WhatsAppMessageRequest):
    """Send WhatsApp text message"""
    result = await whatsapp_client.send_text_message(request.to_number, request.message)
    if result:
        return {"success": True, "message_id": result.get("messages", [{}])[0].get("id")}
    raise HTTPException(status_code=500, detail="Failed to send message")

@router.post("/send-template")
async def send_template(request: WhatsAppMessageRequest):
    """Send WhatsApp template message"""
    result = await whatsapp_client.send_template_message(
        request.to_number, 
        request.template_name, 
        request.language_code
    )
    if result:
        return {"success": True, "message_id": result.get("messages", [{}])[0].get("id")}
    raise HTTPException(status_code=500, detail="Failed to send template")

@router.post("/booking-confirmation")
async def booking_confirmation(request: BookingConfirmationRequest):
    """Send booking confirmation via WhatsApp"""
    result = await send_whatsapp_booking_confirmation(
        request.to_number,
        request.customer_name,
        request.service,
        request.date,
        request.time,
        request.booking_ref
    )
    if result:
        return {"success": True, "message": "Confirmation sent"}
    raise HTTPException(status_code=500, detail="Failed to send confirmation")

@router.post("/send-reminder")
async def send_reminder(request: ReminderRequest):
    """Send appointment reminder via WhatsApp"""
    result = await send_whatsapp_reminder(
        request.to_number,
        request.customer_name,
        request.service,
        request.time
    )
    if result:
        return {"success": True, "message": "Reminder sent"}
    raise HTTPException(status_code=500, detail="Failed to send reminder")

@router.get("/status")
async def get_status():
    """Get WhatsApp service status"""
    return {
        "status": "active" if not whatsapp_client.mock_mode else "mock_mode",
        "mock_mode": whatsapp_client.mock_mode,
        "phone_number_id": whatsapp_client.phone_number_id or "not_configured"
    }
