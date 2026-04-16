import os
from twilio.rest import Client
from config import settings

TWILIO_ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBER = settings.TWILIO_PHONE_NUMBER

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID != "mock_sid" else None

def send_booking_sms(to_number: str, customer_name: str, service: str, time: str):
    if not client:
        print(f"Twilio not configured. MOCK SMS: To {to_number}: Hi {customer_name}, your {service} at {time} is confirmed!")
        return None
        
    try:
        message = client.messages.create(
            body=f"Hi {customer_name}! Your booking for {service} is confirmed for {time}. See you then!",
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )
        return message.sid
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        return None
