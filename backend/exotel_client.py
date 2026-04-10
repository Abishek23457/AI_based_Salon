"""
Exotel Client for BookSmart AI
Handles SMS sending and voice call management through Exotel API
"""
import os
import httpx
from typing import Optional, Dict, Any
from config import settings

class ExotelClient:
    def __init__(self):
        self.account_sid = settings.EXOTEL_ACCOUNT_SID
        self.api_key = settings.EXOTEL_API_KEY
        self.api_token = settings.EXOTEL_API_TOKEN
        self.app_id = settings.EXOTEL_APP_ID
        self.exotel_number = settings.EXOTEL_PHONE_NUMBER
        self.base_url = f"https://api.exotel.com/v1/Accounts/{self.account_sid}"
        self.auth = (self.api_key, self.api_token)
        
        # Mock mode if credentials not set
        self.mock_mode = not all([self.account_sid, self.api_key, self.api_token])
        
    async def send_sms(self, to_number: str, message: str, from_number: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Send SMS via Exotel API"""
        if self.mock_mode:
            print(f"[Exotel MOCK] SMS to {to_number}: {message}")
            return {"sid": "mock_sms_sid", "status": "sent"}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/Sms/send"
                data = {
                    "From": from_number or self.exotel_number,
                    "To": to_number,
                    "Body": message
                }
                
                response = await client.post(url, data=data, auth=self.auth)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"[Exotel] SMS sent successfully: {result.get('SMSMessage', {}).get('Sid')}")
                    return result
                else:
                    print(f"[Exotel] Failed to send SMS: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"[Exotel] SMS sending error: {e}")
            return None
    
    async def make_call(self, to_number: str, app_name: str = None, from_number: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Initiate voice call via Exotel API"""
        if self.mock_mode:
            print(f"[Exotel MOCK] Call to {to_number} using app {app_name or self.app_id}")
            return {"sid": "mock_call_sid", "status": "in-progress"}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/Calls/connect"
                data = {
                    "From": from_number or self.exotel_number,
                    "To": to_number,
                    "CallerId": from_number or self.exotel_number,
                    "Url": f"http://api.exotel.com/v1/Accounts/{self.account_sid}/Apps/{app_name or self.app_id}"
                }
                
                response = await client.post(url, data=data, auth=self.auth)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"[Exotel] Call initiated: {result.get('Call', {}).get('Sid')}")
                    return result
                else:
                    print(f"[Exotel] Failed to initiate call: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"[Exotel] Call initiation error: {e}")
            return None
    
    async def get_call_details(self, call_sid: str) -> Optional[Dict[str, Any]]:
        """Get call details from Exotel"""
        if self.mock_mode:
            return {"sid": call_sid, "status": "completed", "duration": "120"}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/Calls/{call_sid}"
                response = await client.get(url, auth=self.auth)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"[Exotel] Failed to get call details: {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"[Exotel] Call details error: {e}")
            return None

# Initialize Exotel client
exotel_client = ExotelClient()

async def send_booking_sms(to_number: str, customer_name: str, service: str, time: str) -> Optional[Dict[str, Any]]:
    """Send booking confirmation SMS"""
    message = f"Hi {customer_name}! Your booking for {service} is confirmed for {time}. See you then!"
    return await exotel_client.send_sms(to_number, message)

async def send_reminder_sms(to_number: str, customer_name: str, service: str, time: str) -> Optional[Dict[str, Any]]:
    """Send appointment reminder SMS"""
    message = f"Reminder: Hi {customer_name}, you have a {service} appointment at {time} tomorrow. Reply CANCEL to reschedule."
    return await exotel_client.send_sms(to_number, message)
