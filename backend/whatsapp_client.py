"""
WhatsApp Business API Client for BookSmart AI
Handles WhatsApp messaging for bookings, reminders, and notifications
"""
import os
import httpx
from typing import Optional, Dict, Any
from config import settings
import logging

logger = logging.getLogger(__name__)

class WhatsAppClient:
    def __init__(self):
        self.api_key = getattr(settings, 'WHATSAPP_API_KEY', os.getenv('WHATSAPP_API_KEY', ''))
        self.phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', os.getenv('WHATSAPP_PHONE_NUMBER_ID', ''))
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}"
        
        # Mock mode if credentials not set
        self.mock_mode = not all([self.api_key, self.phone_number_id])
        
    async def send_template_message(self, to_number: str, template_name: str, language_code: str = "en", components: list = None) -> Optional[Dict[str, Any]]:
        """Send WhatsApp template message"""
        if self.mock_mode:
            logger.info(f"[WhatsApp MOCK] Template '{template_name}' to {to_number}")
            return {"messages": [{"id": "mock_wa_msg_id"}], "status": "sent"}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/messages"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": to_number,
                    "type": "template",
                    "template": {
                        "name": template_name,
                        "language": {"code": language_code}
                    }
                }
                
                if components:
                    payload["template"]["components"] = components
                
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"[WhatsApp] Message sent: {result.get('messages', [{}])[0].get('id')}")
                    return result
                else:
                    logger.error(f"[WhatsApp] Failed to send: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"[WhatsApp] Error sending message: {e}")
            return None
    
    async def send_text_message(self, to_number: str, message: str) -> Optional[Dict[str, Any]]:
        """Send simple text message"""
        if self.mock_mode:
            logger.info(f"[WhatsApp MOCK] Text to {to_number}: {message[:50]}...")
            return {"messages": [{"id": "mock_wa_msg_id"}], "status": "sent"}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/messages"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": to_number,
                    "type": "text",
                    "text": {"body": message}
                }
                
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"[WhatsApp] Text sent: {result.get('messages', [{}])[0].get('id')}")
                    return result
                else:
                    logger.error(f"[WhatsApp] Failed to send text: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"[WhatsApp] Error: {e}")
            return None
    
    async def send_booking_confirmation(self, to_number: str, customer_name: str, service: str, date: str, time: str, booking_ref: str) -> Optional[Dict[str, Any]]:
        """Send booking confirmation via WhatsApp"""
        message = f"Hi {customer_name}! ✅\n\nYour booking is confirmed:\n📅 {service}\n🗓️ {date} at {time}\n📋 Ref: {booking_ref}\n\nThank you for choosing BookSmart AI!"
        return await self.send_text_message(to_number, message)
    
    async def send_booking_reminder(self, to_number: str, customer_name: str, service: str, time: str) -> Optional[Dict[str, Any]]:
        """Send appointment reminder"""
        message = f"⏰ Reminder: Hi {customer_name}, you have a {service} appointment today at {time}. See you soon!"
        return await self.send_text_message(to_number, message)
    
    async def send_promotional_message(self, to_number: str, offer_text: str) -> Optional[Dict[str, Any]]:
        """Send promotional offer"""
        message = f"🎉 Special Offer! {offer_text}\n\nBook now via BookSmart AI!"
        return await self.send_text_message(to_number, message)

# Initialize WhatsApp client
whatsapp_client = WhatsAppClient()

# Convenience functions
async def send_whatsapp_booking_confirmation(to_number: str, customer_name: str, service: str, date: str, time: str, booking_ref: str):
    """Send booking confirmation via WhatsApp"""
    return await whatsapp_client.send_booking_confirmation(to_number, customer_name, service, date, time, booking_ref)

async def send_whatsapp_reminder(to_number: str, customer_name: str, service: str, time: str):
    """Send appointment reminder via WhatsApp"""
    return await whatsapp_client.send_booking_reminder(to_number, customer_name, service, time)

async def send_whatsapp_promotion(to_number: str, offer_text: str):
    """Send promotional message via WhatsApp"""
    return await whatsapp_client.send_promotional_message(to_number, offer_text)
